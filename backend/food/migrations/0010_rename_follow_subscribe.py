# Generated by Django 3.2.16 on 2024-10-07 11:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("food", "0009_auto_20241004_1330"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Follow",
            new_name="Subscribe",
        ),
    ]
