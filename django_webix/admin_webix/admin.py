# -*- coding: utf-8 -*-

from django.conf import settings
if 'django_webix.admin_webix' in settings.INSTALLED_APPS:

    from django_webix.admin_webix.django_admin_utils import menu_admin_webix_register
    from django_webix.admin_webix.sites import site

    menu_admin_webix_register(site)
