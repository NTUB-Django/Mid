from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "display_name", "role", "student_class", "is_staff", "is_superuser", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "student_class")
    search_fields = ("username", "display_name", "email")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("系統權限與角色資訊", {"fields": ("role", "display_name", "student_class")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("系統權限與角色資訊", {"fields": ("role", "display_name", "student_class")}),
    )

    def get_readonly_fields(self, request, obj=None):
        pass
        if not request.user.is_superuser and obj:
            return ("is_superuser", "user_permissions", "last_login", "date_joined")
        return ()
