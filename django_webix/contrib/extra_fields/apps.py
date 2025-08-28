import sys

from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.db import connection, models
from django.utils.translation import gettext_lazy as _
from django_webix.contrib.extra_fields.fields import NotDbColumnField


class ExtraFieldsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.extra_fields"
    label = "dwextra_fields"
    verbose_name = _("Django Webix Extra Fields")

    def ready(self):
        if "makemigrations" not in sys.argv and not any("migrate" in arg for arg in sys.argv):
            if "dwextra_fields_modelfield" in connection.introspection.table_names():
                from django_webix.contrib.extra_fields.models import ModelField

                # cache mode
                if getattr(settings, "WEBIX_EXTRA_FIELDS_ENABLE_CACHE", False):
                    from django.contrib.contenttypes.models import ContentType
                    from django_webix.contrib.extra_fields.utils_cache import set_cache_extra_fields

                    # set cache only one time
                    set_cache_extra_fields(force=False)

                    # use cache
                    extra_fields = cache.get("django_webix_extra_fields", {})
                    for content_type_id, fields_config in extra_fields.items():
                        content_type = ContentType.objects.get(id=content_type_id)
                        _model = content_type.model_class()

                        for field_config in fields_config:
                            field_class = getattr(models, field_config["field_type"])

                            class CustomNotDbColumnField(NotDbColumnField, field_class):
                                pass

                            if field_config["field_type"] != "ForeignKey":
                                _field = CustomNotDbColumnField(
                                    blank=True, null=True, verbose_name=field_config["label"]
                                )
                            else:
                                related_to_content_type = ContentType.objects.get(id=field_config["related_to"])
                                related_to_class = related_to_content_type.model_class()
                                _field = CustomNotDbColumnField(
                                    related_to_class, blank=True, null=True, verbose_name=field_config["label"]
                                )
                            # private_only=True prevent migrations not required
                            _field.contribute_to_class(_model, field_config["field_name"], private_only=True)

                # database mode
                else:

                    for mf in ModelField.objects.all():
                        _model = mf.content_type.model_class()
                        field_class = getattr(models, mf.field_type)

                        class CustomNotDbColumnField(NotDbColumnField, field_class):
                            pass

                        if mf.field_type != "ForeignKey":
                            _field = CustomNotDbColumnField(blank=True, null=True, verbose_name=mf.label)
                        else:
                            related_to_class = mf.related_to.model_class()
                            _field = CustomNotDbColumnField(
                                related_to_class, blank=True, null=True, verbose_name=mf.label
                            )
                        # private_only=True prevent migrations not required
                        _field.contribute_to_class(_model, mf.field_name, private_only=True)
