# Generated by Django 3.2.16 on 2024-09-16 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("food", "0003_alter_tag_color"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="color",
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(
                help_text="Введите название тега",
                max_length=32,
                unique=True,
                verbose_name="Название тега",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.SlugField(
                help_text="Укажите уникальный слаг",
                max_length=32,
                unique=True,
                verbose_name="Уникальный слаг",
            ),
        ),
    ]