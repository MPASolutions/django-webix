#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import NoReverseMatch
from django.conf import settings
from tests.app_name.models import UrlsModel
from django_webix.apps import check_settings
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.core import management
import django


class TestUrlsCalls(TestCase):

    def setUp(self):
        self.object = UrlsModel.objects.create(field='Test')

    def test_settings_WEBIX_VERSION(self):# not works
        settings.WEBIX_VERSION = None
        check_settings()
        self.assertEqual(settings.WEBIX_VERSION, None)

    def test_settings_app_django_webix_admin_webix(self):# not works
        settings.INSTALLED_APPS.remove('django_webix.admin_webix')
        apps.app_configs = OrderedDict()
        apps.apps_ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)
        from django_webix.admin_webix import admin
        django.setup()

