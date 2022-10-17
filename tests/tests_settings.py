#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.urls import NoReverseMatch
from django.conf import settings
from tests.app_name.models import UrlsModel
from django_webix.apps import check_settings

class TestUrlsCalls(TestCase):

    def setUp(self):
        self.object = UrlsModel.objects.create(field='Test')

    def test_settings_WEBIX_VERSION(self):# not works
        settings.WEBIX_VERSION = None
        check_settings()
        self.assertEqual(settings.WEBIX_VERSION, None)
