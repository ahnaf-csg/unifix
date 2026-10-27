"""Forms for the two-step New complaint page (S-02, docs/03 §6).

Step 1 (LocationForm): category, building, room → duplicate check.
Step 2 (ComplaintForm): the same three fields, carried over as hidden inputs
and checked again, plus title, description and attachments.
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import ALLOWED_FILE_TYPES, MAX_FILES, Category, Complaint, check_attachment_file


class MultipleFileInput(forms.FileInput):
    """A file input that lets the student pick several files at once."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Returns a list of uploaded files (possibly empty) instead of one file."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else ([data] if data else [])
        return [super(MultipleFileField, self).clean(f, initial) for f in files]


class LocationForm(forms.Form):
    """Step 1: what and where. Only active categories of active departments."""

    category = forms.ChoiceField(label="Category")
    building = forms.ChoiceField(
        label="Building", choices=[("", "Choose a building")] + Complaint.Building.choices
    )
    room = forms.CharField(
        label="Room", max_length=30, required=False, help_text="Room label only, e.g. 512 or L3."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.filter(is_active=True, department__is_active=True).select_related(
            "department"
        )
        self.categories = {str(category.pk): category for category in categories}
        # Group the options by department (<optgroup>): the routing is visible while choosing.
        groups = {}
        for category in categories:
            groups.setdefault(category.department.name, []).append((str(category.pk), category.name))
        self.fields["category"].choices = [("", "Choose a category")] + list(groups.items())

    def clean_category(self):
        # ChoiceField has already checked the value is one of the active categories.
        return self.categories[self.cleaned_data["category"]]

    def clean_room(self):
        return self.cleaned_data["room"].strip()


class ComplaintForm(LocationForm):
    """Step 2: details and evidence. Location fields arrive as hidden inputs."""

    title = forms.CharField(label="Title", max_length=120)
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows": 5}))
    attachments = MultipleFileField(
        label="Attachments",
        widget=MultipleFileInput(attrs={"accept": ",".join(ALLOWED_FILE_TYPES), "data-file-list": "file-list"}),
        help_text=f"JPG, PNG, WEBP, MP4, MOV or PDF · up to 15 MB each · at most {MAX_FILES} files.",
    )

    def clean_attachments(self):
        files = self.cleaned_data["attachments"]
        if len(files) > MAX_FILES:
            raise ValidationError(f"You can attach at most {MAX_FILES} files.")  # VR-07
        errors = []
        for uploaded_file in files:
            try:
                check_attachment_file(uploaded_file)  # VR-07: type, content and size
            except ValidationError as error:
                errors.extend(error.messages)
        if errors:
            raise ValidationError(errors)
        return files

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        if category and category.requires_attachment and not cleaned_data.get("attachments") and "attachments" not in self.errors:
            self.add_error("attachments", "This category needs at least one photo, video or PDF.")  # VR-08
        return cleaned_data
