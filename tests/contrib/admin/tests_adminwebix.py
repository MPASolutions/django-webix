#!/usr/bin/env python
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django_webix.contrib.admin.models import WebixAdminMenu

from django_webix.contrib.admin.admin_webix import UserAdmin, GroupAdmin

from django_webix.contrib.admin.decorators import register
from django_webix.contrib import admin
from tests.app_name.models import MyModel


class TestAdminWebixCalls(TestCase):
    def setUp(self):

        WebixAdminMenu.objects.update_or_create(label='test')

        self.object = None
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='12345',
            is_staff=True,
            is_superuser=True,
            is_active=True)
        self.group1 = Group(name='test')
        self.group1.save()

    def test_site(self):
        class TestAdminWebixSite(LazyObject):
            def _setup(self):
                AdminWebixSiteClass = import_string(apps.get_app_config('admin_webix').default_site)
                AdminWebixSiteClass.site_title = "Test"
                AdminWebixSiteClass.index_title = "Test"
                self._wrapped = AdminWebixSiteClass()
        site = TestAdminWebixSite()
        self.assertNotEqual(site, None)


    def test_modeladmin_list(self):
        self.client.login(username='testuser1',
                          password='12345')
        _url = reverse('django_webix.admin:app_name.mymodel.list')
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)

    def test_user_group_modeladmin_list(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()
        _url = reverse('django_webix.admin:{}.{}.list'.format(User._meta.app_label,
                                                       User._meta.model_name))
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)

    def test_user_group_update(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()
        _url = reverse('django_webix.admin:{}.{}.update'.format(User._meta.app_label,
                                                       User._meta.model_name), kwargs={'pk':self.group1.pk})
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)

    def test_user_group_modeladmin_list_json(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()
        _url = reverse('django_webix.admin:{}.{}.list'.format(User._meta.app_label,
                                                       User._meta.model_name))
        response = self.client.post(_url+'?json=true', {
            'QXSPRESETFILTER': '',
            'QXSCLASSESFILTER': '',
            'OTFFILTER': '',
            'ADVANCEDFILTER':'',
            'locked':'{"operator":"AND","qsets":[{"path":"id","val":"1"}]}',
            'location': '',
            'start':0,
            'count': 100,
            'filters': {},
        })
        self.assertEqual(response.status_code, 200)

    def test_failed_register_model(self):
        @admin.register(None, site=None)
        class MyModelAdmin(admin.ModelWebixAdmin):
            pass

    def test_user_menu_list(self):
        self.client.login(username='testuser1',
                          password='12345')
        _url = reverse('admin:{}_{}_changelist'.format(WebixAdminMenu._meta.app_label,
                                                       WebixAdminMenu._meta.model_name))
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)

    def test_user_menu_create(self):
        self.client.login(username='testuser1',
                          password='12345')
        _url = reverse('admin:{}_{}_add'.format(WebixAdminMenu._meta.app_label,
                                                WebixAdminMenu._meta.model_name))
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 200)

    def test_user_modeladmin_create(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()
        _url = reverse('django_webix.admin:{}.{}.create'.format(User._meta.app_label,
                                                         User._meta.model_name))
        response = self.client.post(_url, {
            'username': 'testttt',
            'password1': 'test',
            'password2': 'test',
        })
        self.assertEqual(response.status_code, 302) # redirect

    def test_user_modeladmin_create_passwordfailed(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()
        _url = reverse('django_webix.admin:{}.{}.create'.format(User._meta.app_label,
                                                       User._meta.model_name))
        response = self.client.post(_url, {
            'username': 'testttt1',
            'password1': 'test',
            'password2': 'test2',
        })
        self.assertEqual(response.status_code, 200)

    def test_user_modeladmin_update(self):
        self.client.login(username='testuser1',
                          password='12345')
        User = get_user_model()

        _url = reverse('django_webix.admin:{}.{}.update'.format(User._meta.app_label,
                                                         User._meta.model_name), kwargs={'pk':self.user1.pk})
        response = self.client.post(_url, {
            'password1': '12345',
            'password2': '12345',
        })
        self.assertEqual(response.status_code, 200)

    def test_user_modeladmin_passwordchange(self):
        self.client.login(username='testuser1',
                          password='12345')
        _url = reverse('django_webix.admin:password_change', kwargs={'pk':self.user1.pk})
        response = self.client.post(_url, {
            'password1': '12345',
            'password2': '12345',
        })
        self.assertEqual(response.status_code, 200)
