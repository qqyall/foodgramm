# Generated by Django 3.2.16 on 2024-09-10 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_avatar_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="avatar_image",
        ),
    ]
