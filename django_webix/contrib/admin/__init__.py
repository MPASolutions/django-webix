from django.utils.module_loading import autodiscover_modules
from django_webix.contrib.admin.decorators import register
from django_webix.contrib.admin.options import ModelWebixAdmin
from django_webix.contrib.admin.sites import AdminWebixSite, site

__all__ = [
    "register",
    "ModelWebixAdmin",
    "AdminWebixSite",
    "site",
    "autodiscover",
]


def autodiscover():
    autodiscover_modules("dwadmin", register_to=site)


default_app_config = "django_webix.contrib.admin.apps.AdminConfig"
