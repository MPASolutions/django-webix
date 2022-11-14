from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.auth"
    label = 'dwauth'
    verbose_name = _("Django Webix Authentication and Authorization")
