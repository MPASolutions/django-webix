# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SimpleAdminWebixConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_site = 'django_webix.admin_webix.sites.AdminWebixSite'
    name = 'django_webix.admin_webix'
    verbose_name = _("Administration")

    def ready(self):
        # checks.register(check_dependencies, checks.Tags.admin) # TODO
        # checks.register(check_admin_app, checks.Tags.admin) # TODO
        pass


class AdminWebixConfig(SimpleAdminWebixConfig):
    """The default AppConfig for admin which does autodiscovery."""

    def ready(self):
        super().ready()
        self.module.autodiscover()
