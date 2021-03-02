# -*- coding: utf-8 -*-

from django_webix.admin_webix.decorators import register
from django_webix.admin_webix.options import ModelWebixAdmin
from django_webix.admin_webix.sites import AdminWebixSite, site
from django.utils.module_loading import autodiscover_modules

__all__ = [
    "register", "ModelWebixAdmin", "AdminWebixSite", "site", "autodiscover",
]


def autodiscover():
    autodiscover_modules('admin_webix', register_to=site)


default_app_config = 'django_webix.admin_webix.apps.AdminWebixConfig'
