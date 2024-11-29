from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CommandsManagerConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_webix.contrib.commands_manager"
    label = "dwcommands_manager"
    verbose_name = _("Django Webix Commands Manager")

    def ready(self):

        # CHECK settings
        if not hasattr(settings, "DJANGO_WEBIX_COMMANDS_MANAGER_APP_CELERY"):
            raise Exception("DJANGO_WEBIX_COMMANDS_MANAGER_APP_CELERY configuration is not found in your settings")
