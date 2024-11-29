from django.apps import AppConfig
from django.db import connection, models
from django.utils.translation import gettext_lazy as _
from django_webix.contrib.extra_fields.fields import NotDbColumnField


class ExtraFieldsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.extra_fields"
    label = "dwextra_fields"
    verbose_name = _("Django Webix Extra Fields")

    def ready(self):
        if "dwextra_fields_modelfield" in connection.introspection.table_names():
            from django_webix.contrib.extra_fields.models import ModelField

            for mf in ModelField.objects.all():
                _model = mf.content_type.model_class()
                field_class = getattr(models, mf.field_type)

                class CustomNotDbColumnField(NotDbColumnField, field_class):
                    pass

                if mf.field_type != "ForeignKey":
                    _field = CustomNotDbColumnField(blank=True, null=True, verbose_name=mf.label)
                else:
                    related_to_class = mf.related_to.model_class()
                    _field = CustomNotDbColumnField(related_to_class, blank=True, null=True, verbose_name=mf.label)
                # private_only=True prevent migrations not required
                _field.contribute_to_class(_model, mf.field_name, private_only=True)
