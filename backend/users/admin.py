from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    Админ-зона пользователя.
    """

    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "avatar",
    )
    search_fields = ("username", "email")
    list_filter = (
        "username",
        "email",
    )
    empty_value_display = "-"
