# Generated by Django 5.0.3 on 2024-05-27 12:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dwextra_fields", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="modelfield",
            name="field_name",
            field=models.CharField(
                max_length=64,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Field name must not contain spaces and special characters, and must begin with a letter",
                        regex="^[a-zA-Z]+[\\w-]*$",
                    )
                ],
                verbose_name="Field name",
            ),
        ),
    ]