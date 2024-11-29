#!/usr/bin/env python

from collections import OrderedDict

import django
from django.apps import apps
from django.conf import settings
from django.test import TestCase
from tests.app_name.models import UrlsModel


class TestUrlsCalls(TestCase):

    def setUp(self):
        self.object = UrlsModel.objects.create(field="Test")

    def test_settings_WEBIX_VERSION(self):  # not works
        settings.WEBIX_VERSION = None
        # check_settings()
        self.assertEqual(settings.WEBIX_VERSION, None)

    def test_settings_app_django_webix_admin_webix(self):  # not works
        settings.INSTALLED_APPS.remove("django_webix.contrib.admin")
        apps.app_configs = OrderedDict()
        apps.apps_ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)

        django.setup()
