#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.apps import apps
from django.test import TestCase
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django_webix.admin_webix.decorators import register
from django_webix import admin_webix as admin

from tests.app_name.models import MyModel


class TestAdminWebixCalls(TestCase):
    def setUp(self):
        self.object = None

    def test_set_site(self):
        class TestAdminWebixSite(LazyObject):
            def _setup(self):
                AdminWebixSiteClass = import_string(apps.get_app_config('admin_webix').default_site)


                AdminWebixSiteClass.site_title = "Test"
                AdminWebixSiteClass.index_title = "Test"


                self._wrapped = AdminWebixSiteClass()
        site = TestAdminWebixSite()
        self.assertNotEqual(site, None)

    def test_set_modeladmin(self):
        @admin.register(MyModel)
        class MyModelAdmin(admin.ModelAdmin):
            pass
