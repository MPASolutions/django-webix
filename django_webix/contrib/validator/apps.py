from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ValidatorConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.validator"
    label = 'dwvalidator'
    verbose_name = _("Django Webix Validator")
