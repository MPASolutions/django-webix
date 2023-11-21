# Generated by Django 4.2.7 on 2023-11-07 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModelField",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=255, verbose_name="Description")),
                (
                    "field_name",
                    models.CharField(max_length=64, verbose_name="Field name"),
                ),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("IntegerField", "INTEGERFIELD"),
                            ("FloatField", "FLOATFIELD"),
                            ("BooleanField", "BOOLEANFIELD"),
                            ("CharField", "CHARFIELD"),
                            ("DateField", "DATEFIELD"),
                        ],
                        max_length=64,
                        verbose_name="Field type",
                    ),
                ),
                (
                    "locked",
                    models.BooleanField(
                        blank=True, default=False, verbose_name="Locked"
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                        verbose_name="Model",
                    ),
                ),
                (
                    "related_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_fields_related_to",
                        to="contenttypes.contenttype",
                        verbose_name="Model for FK",
                    ),
                ),
            ],
            options={
                "verbose_name": "Model field",
                "verbose_name_plural": "Model fields",
                "unique_together": {("content_type", "field_name")},
            },
        ),
        migrations.CreateModel(
            name="ModelFieldValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "object_id",
                    models.PositiveIntegerField(
                        db_index=True, verbose_name="Object ID"
                    ),
                ),
                ("value", models.TextField(blank=True, verbose_name="Value")),
                (
                    "locked",
                    models.BooleanField(
                        blank=True, default=False, verbose_name="Locked"
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                        verbose_name="Content type",
                    ),
                ),
                (
                    "model_field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dwextra_fields.modelfield",
                        verbose_name="Model field",
                    ),
                ),
            ],
            options={
                "verbose_name": "Model field value",
                "verbose_name_plural": "Model fields values",
                "unique_together": {("content_type", "object_id", "model_field")},
                "index_together": {
                    ("content_type", "object_id", "model_field"),
                    ("content_type", "object_id"),
                },
            },
        ),
        migrations.CreateModel(
            name="ModelFieldChoice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.TextField(blank=True, verbose_name="Key")),
                ("value", models.TextField(blank=True, verbose_name="Value")),
                (
                    "model_field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dwextra_fields.modelfield",
                        verbose_name="Model field",
                    ),
                ),
            ],
            options={
                "verbose_name": "Model field choice",
                "verbose_name_plural": "Model fields choices",
                "unique_together": {("model_field", "key")},
            },
        ),
    ]
