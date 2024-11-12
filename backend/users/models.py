from django.contrib.auth.models import AbstractUser
from django.db import models

from . import constants


class User(AbstractUser):
    """
    Кастомизированная модель пользователя.
    Регистрация с помощью email.
    """

    username = models.CharField(
        verbose_name="Логин",
        max_length=constants.MAX_LEN_USERNAME,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=constants.MAX_LEN_FIRST_NAME
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=constants.MAX_LEN_LAST_NAME
    )
    email = models.EmailField(verbose_name="email-адрес", unique=True)
    password = models.CharField(
        max_length=constants.MAX_LEN_PASSWORD, verbose_name="Пароль"
    )
    avatar = models.ImageField(upload_to="users/", null=True, default=None)

    REQUIRED_FIELDS = ["username", "password", "first_name", "last_name"]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
