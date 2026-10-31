"""Inline action forms on A-03 (docs/04 A-03, docs/05 §2).

The forms only collect and tidy the input. The rules (VR-03 to VR-05, who may
act) are checked again by the Complaint methods, which the view calls.
"""

from datetime import timedelta

from django import forms
from django.utils import timezone

from complaints.models import PROOF_FILE_TYPES, Complaint


class VerifyForm(forms.Form):
    """Verify: priority and a due date later than today (C-06, VR-05)."""

    priority = forms.ChoiceField(choices=Complaint.Priority.choices)
    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The browser's date picker starts at tomorrow; the server still checks (VR-05).
        tomorrow = timezone.localdate() + timedelta(days=1)
        self.fields["due_date"].widget.attrs["min"] = tomorrow.isoformat()

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]
        if due_date <= timezone.localdate():
            raise forms.ValidationError("The due date must be later than today.")
        return due_date


class RejectForm(forms.Form):
    """Reject: a reason is required (VR-04). The reporter sees it."""

    reason = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), help_text="The student sees this reason.")


class StartWorkForm(forms.Form):
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Note (optional)",
        help_text="Shown to the student in the timeline.",
    )


class ResolveForm(forms.Form):
    """Mark resolved: a note is required (VR-04); one proof photo is optional (C-07)."""

    note = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label="What was done",
        help_text="Shown to the student in the timeline.",
    )
    proof_file = forms.FileField(
        required=False,
        label="Proof photo (optional)",
        help_text="One JPG, PNG or WEBP photo, at most 15 MB.",
        widget=forms.ClearableFileInput(attrs={"accept": ",".join(sorted(PROOF_FILE_TYPES))}),
    )


class NoteForm(forms.Form):
    """Add note: public (the reporter sees it) or internal (admins only), C-08."""

    VISIBILITY_CHOICES = [("public", "Public: the student sees it"), ("internal", "Internal: admins only")]

    note = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES, initial="public", widget=forms.RadioSelect)


# URL action slug → form (docs/05 action mapping). Start review needs no input.
ACTION_FORMS = {
    "verify": VerifyForm,
    "reject": RejectForm,
    "start_work": StartWorkForm,
    "resolve": ResolveForm,
    "note": NoteForm,
}
