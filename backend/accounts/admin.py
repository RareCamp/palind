from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Organization


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "email",
        "first_name",
        "last_name",
        "organization",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "organization",
        "is_active",
    )
    fieldsets = (
        ("Login info", {"fields": ("email", "password", "is_active")}),
        ("Organization", {"fields": ("organization",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "picture")}),
        ("Permissions", {"fields": ("is_staff",)}),
    )
    add_fieldsets = (
        ("Login info", {"fields": ("email", "password1", "password2", "is_active")}),
        ("Organization", {"fields": ("organization",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "picture")}),
    )
    search_fields = ("email",)
    ordering = ("email",)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "users_list")

    def users_list(self, obj):
        return ", ".join([u.email for u in obj.users.all()])


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
