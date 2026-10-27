"""Admin console views, URL namespace `console` (docs/05 §2, §4).

Every view is for admins only (@admin_required). Complaints are loaded through
get_complaint_for_user(), so a Dept Admin gets 404 for other departments
(VR-02). Actions only call Complaint methods, which check the rules again.
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.permissions import admin_required, get_complaint_for_user
from complaints.models import Attachment, Category, Complaint, ComplaintUpdate, Department
from complaints.views import send_attachment

from .forms import ACTION_FORMS


def visible_complaints(user):
    """Own department for a Dept Admin, all for the Super Admin (VR-02)."""
    complaints = Complaint.objects.select_related("category", "department", "reporter")
    if user.is_super_admin():
        return complaints
    return complaints.filter(department_id=user.department_id)


@admin_required
def dashboard(request):
    """A-01 Dashboard. Placeholder until Sprint 4 (cards, tables and charts follow).

    Dept Admins see their own department; the Super Admin sees all departments (VR-02).
    """
    if request.user.is_super_admin():
        departments = Department.objects.all()
    else:
        departments = Department.objects.filter(pk=request.user.department_id)
    departments = departments.prefetch_related("categories")
    return render(request, "console/dashboard.html", {"departments": departments})


@admin_required
def queue(request):
    """A-02 Complaint queue with filters, search and sort (docs/04 A-02).

    All filters are GET parameters, so a filtered queue can be bookmarked.
    """
    complaints = visible_complaints(request.user).annotate(supporters=Count("supports"))
    params = request.GET

    status = params.get("status", "open")
    if status == "open":
        complaints = complaints.filter(status__in=Complaint.OPEN_STATUSES)
    elif status in Complaint.Status.values:
        complaints = complaints.filter(status=status)
    else:
        status = "all"

    categories = Category.objects.select_related("department")
    departments = Department.objects.all()
    if not request.user.is_super_admin():
        categories = categories.filter(department_id=request.user.department_id)
    department = params.get("department", "")
    if request.user.is_super_admin() and department.isdigit():
        complaints = complaints.filter(department_id=department)
    category = params.get("category", "")
    if category.isdigit():
        complaints = complaints.filter(category_id=category)
    priority = params.get("priority", "")
    if priority in Complaint.Priority.values:
        complaints = complaints.filter(priority=priority)
    overdue = params.get("overdue") == "1"
    if overdue:
        # The same rule as Complaint.is_overdue (docs/03 §5), as a database filter.
        complaints = complaints.filter(
            due_date__lt=timezone.localdate(),
            status__in=[Complaint.Status.VERIFIED, Complaint.Status.IN_PROGRESS, Complaint.Status.REOPENED],
        )
    query = params.get("q", "").strip()
    if query:
        complaints = complaints.filter(
            Q(tracking_id__icontains=query)
            | Q(title__icontains=query)
            | Q(room__icontains=query)
            | Q(reporter__full_name__icontains=query)
            | Q(reporter__student_id__icontains=query)
            | Q(reporter__email__icontains=query)
        )

    sort = "updated" if params.get("sort") == "updated" else "due"
    if sort == "due":
        # Soonest due date first; complaints without a due date (not verified yet) last.
        complaints = complaints.order_by(F("due_date").asc(nulls_last=True), "-updated_at")
    else:
        complaints = complaints.order_by("-updated_at")

    return render(
        request,
        "console/queue.html",
        {
            "complaints": complaints,
            "status": status,
            "status_choices": Complaint.Status.choices,
            "category": category,
            "categories": categories,
            "department": department,
            "departments": departments,
            "priority": priority,
            "priority_choices": Complaint.Priority.choices,
            "overdue": overdue,
            "query": query,
            "sort": sort,
        },
    )


def history_entries(complaint):
    """Full history for A-03 with actor names; consecutive "Me too" entries grouped (docs/04 A-03)."""
    entries = []
    for update in complaint.updates.select_related("actor"):
        last = entries[-1] if entries else None
        if update.action == ComplaintUpdate.Action.SUPPORT and last and last["is_support"]:
            last["actors"].append(update.actor.full_name)
            continue
        entries.append({
            "action": update.get_action_display(),
            "is_support": update.action == ComplaintUpdate.Action.SUPPORT,
            "actors": [update.actor.full_name],
            "note": update.note,
            "is_internal": update.is_internal,
            "created_at": update.created_at,
        })
    return entries


def render_detail(request, complaint, bound_form=None, open_action="", status=200):
    """A-03 page. After a failed action, `bound_form` is shown open with its errors."""
    buttons = complaint.allowed_actions(request.user)
    form_shown = open_action == "note" and complaint.can_add_note(request.user)
    for button in buttons:
        form_class = ACTION_FORMS.get(button["slug"])
        if button["slug"] == open_action and button["enabled"]:
            button["form"] = bound_form
            form_shown = True
        else:
            button["form"] = form_class() if form_class else None
    # The action is no longer possible (e.g. another admin acted first): its form is
    # not shown, so its errors go above the action bar instead.
    bar_errors = bound_form.non_field_errors() if bound_form is not None and not form_shown else []
    attachments = list(complaint.attachments.all())
    reporter = complaint.reporter
    context = {
        "complaint": complaint,
        "buttons": buttons,
        "open_action": open_action,
        "bar_errors": bar_errors,
        "can_add_note": complaint.can_add_note(request.user),
        "note_form": bound_form if open_action == "note" else ACTION_FORMS["note"](),
        "history": history_entries(complaint),
        "evidence": [a for a in attachments if a.kind == Attachment.Kind.EVIDENCE],
        "proof": [a for a in attachments if a.kind == Attachment.Kind.PROOF_OF_FIX],
        "reporter": reporter,
        "reporter_filed": reporter.complaints.count(),
        "reporter_rejected": reporter.complaints.filter(status=Complaint.Status.REJECTED).count(),
    }
    return render(request, "console/complaint_detail.html", context, status=status)


@admin_required
def complaint_detail(request, tracking_id):
    """A-03 Complaint detail with the action bar and Add note."""
    complaint = get_complaint_for_user(request.user, tracking_id)
    return render_detail(request, complaint)


@admin_required
@require_POST
def complaint_action(request, tracking_id, action):
    """Run one A-03 action (docs/05 action mapping) and come back to A-03.

    Success: a message and a redirect (Post/Redirect/Get). Failure: the page is
    shown again with that form open and its errors.
    """
    if action != "start_review" and action not in ACTION_FORMS:
        raise Http404  # reassign arrives in Sprint 4
    complaint = get_complaint_for_user(request.user, tracking_id)
    form = None
    if action in ACTION_FORMS:
        form = ACTION_FORMS[action](request.POST, request.FILES)
        if not form.is_valid():
            return render_detail(request, complaint, form, action, status=400)
        data = form.cleaned_data
    try:
        if action == "start_review":
            complaint.start_review(request.user)
        elif action == "verify":
            complaint.verify(request.user, data["priority"], data["due_date"])
        elif action == "reject":
            complaint.reject(request.user, data["reason"])
        elif action == "start_work":
            complaint.start_work(request.user, data["note"])
        elif action == "resolve":
            complaint.resolve(request.user, data["note"], data["proof_file"])
        elif action == "note":
            complaint.add_note(request.user, data["note"], is_internal=data["visibility"] == "internal")
    except ValidationError as error:
        if form is None:
            messages.error(request, error.messages[0])
            return redirect("console:complaint_detail", tracking_id=complaint.tracking_id)
        form.add_error(None, error)
        complaint.refresh_from_db()
        return render_detail(request, complaint, form, action, status=400)
    if action == "note":
        messages.success(request, "Note added.")
    else:
        messages.success(request, f"{complaint.tracking_id} is now {complaint.get_status_display()}.")
    return redirect("console:complaint_detail", tracking_id=complaint.tracking_id)


@admin_required
def attachment(request, tracking_id, pk):
    """Console twin of student:attachment (NFR-03): admins who can see the complaint."""
    complaint = get_complaint_for_user(request.user, tracking_id)
    return send_attachment(complaint, pk)
