from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdminConfig(AppConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = "django_webix.contrib.admin.sites.AdminWebixSite"
    name = "django_webix.contrib.admin"
    label = "dwadmin"
    verbose_name = _("Administration")

    def ready(self):
        super().ready()
        self.module.autodiscover()
