from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


#class SimpleAdminConfig(AppConfig):
#    """Simple AppConfig which does not do automatic discovery."""
#
#    default_auto_field = "django.db.models.AutoField"
#    default_site = 'django_webix.contrib.admin.sites.AdminWebixSite'
#    name = 'django_webix.contrib.admin'
#    label = 'dwadmin'
#    verbose_name = _("Administration")
#
#    def ready(self):
#        # checks.register(check_dependencies, checks.Tags.admin) # TODO
#        # checks.register(check_admin_app, checks.Tags.admin) # TODO
#        pass


class AdminConfig(AppConfig): #SimpleAdminConfig):
    """The default AppConfig for admin which does autodiscovery."""

    default_auto_field = "django.db.models.AutoField"
    default_site = 'django_webix.contrib.admin.sites.AdminWebixSite'
    name = 'django_webix.contrib.admin'
    label = 'dwadmin'
    verbose_name = _("Administration")

    def ready(self):
        super().ready()
        self.module.autodiscover()
