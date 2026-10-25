"""Django admin setup (C-16): departments and categories are edited here;
complaints are shown read-only for checking data. Workflow changes go through
the Complaint methods, never the admin."""

from django.contrib import admin

from .models import Attachment, Category, Complaint, ComplaintUpdate, Department, Support


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "code"]
    inlines = [CategoryInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "requires_attachment", "is_active"]
    list_filter = ["department", "requires_attachment", "is_active"]
    search_fields = ["name"]


class ReadOnlyInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AttachmentInline(ReadOnlyInline):
    model = Attachment
    # No file link: files are only sent by the permission-checked view (NFR-03).
    fields = ["original_name", "kind", "mime_type", "size_bytes", "uploaded_by", "uploaded_at"]


class ComplaintUpdateInline(ReadOnlyInline):
    model = ComplaintUpdate
    fields = ["created_at", "actor", "action", "from_status", "to_status", "note", "is_internal"]


class SupportInline(ReadOnlyInline):
    model = Support
    fields = ["student", "created_at"]


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ["tracking_id", "title", "department", "category", "status", "due_date", "created_at"]
    list_filter = ["status", "department", "building"]
    search_fields = ["tracking_id", "title", "room", "reporter__email"]
    inlines = [AttachmentInline, ComplaintUpdateInline, SupportInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
