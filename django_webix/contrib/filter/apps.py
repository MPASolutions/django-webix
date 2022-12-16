from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


class FilterConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.filter"
    label = 'dwfilter'
    verbose_name = _("Django Webix Filter")

    def ready(self):
        if not hasattr(settings, 'DJANGO_WEBIX_FILTER') or not isinstance(settings.DJANGO_WEBIX_FILTER, dict):
            raise ImproperlyConfigured("`DJANGO_WEBIX_FILTER` is not configured in settings")
        if "models" not in settings.DJANGO_WEBIX_FILTER:
            raise ImproperlyConfigured("`models` is not configured in DJANGO_WEBIX_FILTER")
        if "visibility" in settings.DJANGO_WEBIX_FILTER and \
            not isinstance(settings.DJANGO_WEBIX_FILTER["visibility"], dict):
            raise ImproperlyConfigured("`visibility` must be a dict")
        if "shared_edit_groups" in settings.DJANGO_WEBIX_FILTER and \
            not isinstance(settings.DJANGO_WEBIX_FILTER["shared_edit_groups"], dict):
            raise ImproperlyConfigured("`shared_edit_groups` must be a dict")
