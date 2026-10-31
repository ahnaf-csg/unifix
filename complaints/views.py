"""Student-facing views, URL namespace `student` (docs/05 §2, §4).

Views only read data and call Complaint methods; the rules live in the models
(CLAUDE.md). Every complaint page loads its complaint through
accounts.permissions.get_complaint_for_user(), so access is always checked.
"""

from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.permissions import get_complaint_for_user, has_full_view, student_required
from notifications.views import with_links

from .forms import ComplaintForm, LocationForm
from .models import Attachment, Complaint, ComplaintUpdate, Support


def own_and_supported(user):
    """Complaints a student reported or supports (S-01, S-03)."""
    supported = Support.objects.filter(student=user).values("complaint")
    return Complaint.objects.filter(Q(reporter=user) | Q(pk__in=supported)).select_related(
        "category", "department"
    )


@student_required
def home(request):
    """S-01 Student home: cards, needs your action, recent complaints, latest notifications."""
    own = Complaint.objects.filter(reporter=request.user)
    awaiting = own.filter(status=Complaint.Status.RESOLVED).order_by("resolved_at")
    context = {
        "open_count": own.filter(status__in=Complaint.OPEN_STATUSES).count(),
        "awaiting_count": awaiting.count(),
        "closed_count": own.filter(status=Complaint.Status.CLOSED).count(),
        "supported_count": Support.objects.filter(student=request.user).count(),
        "needs_action": awaiting,
        "recent": own_and_supported(request.user).order_by("-updated_at")[:5],
        "latest_notifications": with_links(
            request.user, request.user.notifications.select_related("complaint")[:5]
        ),
    }
    return render(request, "student/home.html", context)


@student_required
def complaint_new(request):
    """S-02 New complaint, in two steps so files are uploaded only once (docs/03 §6).

    GET              step 1: category, building, room
    GET ?step=check  run the duplicate check; show matches, or step 2 if none
    GET ?step=details  step 2 (from "Continue with a new complaint")
    POST             Submit: check everything again, then Complaint.submit()
    """
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            try:
                complaint = Complaint.submit(
                    reporter=request.user,
                    category=data["category"],
                    building=data["building"],
                    room=data["room"],
                    title=data["title"],
                    description=data["description"],
                    files=data["attachments"],
                )
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(
                    request,
                    f"Complaint {complaint.tracking_id} submitted and sent to {complaint.department.name}.",
                )
                return redirect("student:complaint_detail", tracking_id=complaint.tracking_id)
        return render_step_two(request, form)

    step = request.GET.get("step", "")
    if step not in ("check", "details"):
        # Step 1, empty or filled in again from the "Change" link.
        location_form = LocationForm(initial=request.GET.dict())
        return render(request, "student/complaint_form.html", {"step": 1, "location_form": location_form})

    location_form = LocationForm(request.GET)
    if not location_form.is_valid():
        return render(request, "student/complaint_form.html", {"step": 1, "location_form": location_form})
    location = location_form.cleaned_data

    if step == "check":
        matches = Complaint.find_duplicates(location["category"], location["building"], location["room"])
        if matches:
            supported_ids = set(
                Support.objects.filter(student=request.user, complaint__in=matches).values_list(
                    "complaint_id", flat=True
                )
            )
            for match in matches:
                match.is_own = match.reporter_id == request.user.pk
                match.is_supported = match.pk in supported_ids
            return render(
                request,
                "student/complaint_form.html",
                {
                    "step": "matches",
                    "location": location,
                    "matches": matches,
                    "continue_url": step_url("details", location),
                    "change_url": step_url("1", location),
                },
            )

    form = ComplaintForm(
        initial={
            "category": str(location["category"].pk),
            "building": location["building"],
            "room": location["room"],
        }
    )
    return render_step_two(request, form, location)


def step_url(step, location):
    """S-02 URL for a step, carrying category, building and room in the query string."""
    query = {
        "step": step,
        "category": location["category"].pk,
        "building": location["building"],
        "room": location["room"],
    }
    return f"{reverse('student:complaint_new')}?{urlencode(query)}"


def render_step_two(request, form, location=None):
    """Step 2 page. After a failed POST the location comes from the form itself."""
    if location is None:
        if any(field in form.errors for field in ("category", "building", "room")):
            # The carried-over location is no longer valid (e.g. category deactivated): back to step 1.
            messages.error(request, "Please choose the category and location again.")
            return redirect("student:complaint_new")
        location = {field: form.cleaned_data[field] for field in ("category", "building", "room")}
    return render(
        request,
        "student/complaint_form.html",
        {
            "step": 2,
            "form": form,
            "detail_fields": [form["title"], form["description"], form["attachments"]],
            "location": location,
            "building_label": Complaint.Building(location["building"]).label,
            "change_url": step_url("1", location),
        },
    )


@student_required
def complaint_list(request):
    """S-03 My complaints: own and supported, with a status filter and search."""
    complaints = own_and_supported(request.user).order_by("-updated_at")
    status = request.GET.get("status", "")
    if status in Complaint.Status.values:
        complaints = complaints.filter(status=status)
    query = request.GET.get("q", "").strip()
    if query:
        complaints = complaints.filter(
            Q(tracking_id__icontains=query) | Q(title__icontains=query) | Q(room__icontains=query)
        )
    return render(
        request,
        "student/complaint_list.html",
        {
            "complaints": complaints,
            "status": status,
            "query": query,
            "status_choices": Complaint.Status.choices,
        },
    )


def public_actor(update, complaint, viewer):
    """Who did it, as a student may see it: a role or department, never a name (VR-01)."""
    actor = update.actor
    if actor.pk == viewer.pk:
        return "You"
    if update.action == ComplaintUpdate.Action.SUPPORT:
        return "A student"
    if actor.pk == complaint.reporter_id:
        return "Reporter"
    if actor.is_dept_admin() and actor.department:
        return actor.department.name
    return actor.get_role_display()


@student_required
def complaint_detail(request, tracking_id):
    """S-04 Complaint detail: full view for the reporter, limited view for a supporter."""
    complaint = get_complaint_for_user(request.user, tracking_id)
    full_view = has_full_view(request.user, complaint)
    updates = complaint.updates.filter(is_internal=False).select_related("actor__department")
    timeline = [
        {
            "action": update.get_action_display(),
            "actor": public_actor(update, complaint, request.user),
            "note": update.note,
            "created_at": update.created_at,
        }
        for update in updates
    ]
    context = {
        "complaint": complaint,
        "full_view": full_view,
        "timeline": timeline,
    }
    if full_view:
        attachments = list(complaint.attachments.all())
        context["evidence"] = [a for a in attachments if a.kind == Attachment.Kind.EVIDENCE]
        context["proof"] = [a for a in attachments if a.kind == Attachment.Kind.PROOF_OF_FIX]
    return render(request, "student/complaint_detail.html", context)


@student_required
@require_POST
def complaint_action(request, tracking_id, action):
    """Student actions (docs/05 action mapping): "Me too" (support, Sprint 2) and
    withdraw (C-10, Sprint 3); confirm, reopen and rate arrive in Sprint 4."""
    if action == "withdraw":
        return withdraw(request, tracking_id)
    if action != "support":
        raise Http404
    complaint = get_object_or_404(Complaint, tracking_id=tracking_id)
    try:
        complaint.support(request.user)  # VR-09
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(
            request, f"You now support {complaint.tracking_id}. You'll find it under My complaints."
        )
    if request.user.can_view_complaint(complaint):
        return redirect("student:complaint_detail", tracking_id=complaint.tracking_id)
    return redirect("student:complaint_new")


def withdraw(request, tracking_id):
    """C-10: the reporter withdraws a complaint that is still Submitted."""
    complaint = get_complaint_for_user(request.user, tracking_id)  # 404 for others
    try:
        complaint.withdraw(request.user)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, f"{complaint.tracking_id} was withdrawn.")
    return redirect("student:complaint_detail", tracking_id=complaint.tracking_id)


def send_attachment(complaint, pk):
    """Send one of the complaint's files (NFR-03). Used by student:attachment and
    console:attachment, which check permissions first."""
    file = get_object_or_404(complaint.attachments, pk=pk)
    response = FileResponse(file.file.open("rb"), content_type=file.mime_type, filename=file.original_name)
    response["Cache-Control"] = "private"
    return response


@student_required
def attachment(request, tracking_id, pk):
    """Send an evidence or proof file after the permission check (NFR-03).

    Supporters have the limited view, which has no files (VR-01), so they get 404.
    """
    complaint = get_complaint_for_user(request.user, tracking_id)
    if not has_full_view(request.user, complaint):
        raise Http404
    return send_attachment(complaint, pk)
