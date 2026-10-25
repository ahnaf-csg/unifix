"""Django admin setup for departments and categories (C-16)."""

from django.contrib import admin

from .models import Category, Department


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
