#!/usr/bin/env python

from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse
from tests.app_name.models import UrlsModel, MyModel
from django.contrib.auth.models import User, Permission


class TestPermissionsCalls(TestCase):
    def setUp(self):
        self.item = MyModel(**{
            'field': "Test",
            'email': "test@test.it",
            'floatfield': 10.2,
            'decimalfield': 11.56,
            'integerfield': 5,
        })
        self.item.save()
        user1 = User.objects.create_user(username='testuser1',
                                 password='12345')
        user2 = User.objects.create_user(username='testuser2',
                                 password='12345')
        user2.user_permissions.add(Permission.objects.get(codename='add_mymodel'))
        user2.user_permissions.add(Permission.objects.get(codename='change_mymodel'))
        user2.user_permissions.add(Permission.objects.get(codename='view_mymodel'))
        user2.user_permissions.add(Permission.objects.get(codename='delete_mymodel'))


    def test_call_view_create_invalid_post(self):
        self.client.login(username='testuser1',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.create'), {
            'field': "Test",
            'email': "test@test.it",
            'floatfield': 10.2,
            'decimalfield': 11.56,
            'integerfield': 5,
        })
        self.assertEqual(response.status_code, 403)

    def test_call_view_create_successurl_post(self):
        self.client.login(username='testuser2',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.create'), {
            'field': "Test",
            'email': "test@test.it",
            'floatfield': 10.2,
            'decimalfield': 11.56,
            'integerfield': 5,
        })
        self.assertEqual(response.status_code, 302)

    def test_call_view_update_invalid_post(self):
        self.client.login(username='testuser1',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.update', kwargs={'pk':self.item.pk}), {
            'field': "Test",
            'email': "test@test.it",
            'floatfield': 10.2,
            'decimalfield': 11.56,
            'integerfield': 5,
        })
        self.assertEqual(response.status_code, 403)

    def test_call_view_update_successurl_post(self):
        self.client.login(username='testuser2',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.update', kwargs={'pk':self.item.pk}), {
            'field': "Test",
            'email': "test@test.it",
            'floatfield': 10.2,
            'decimalfield': 11.56,
            'integerfield': 5,
        })
        self.assertEqual(response.status_code, 302)

    def test_call_view_delete_invalid_post(self):
        self.client.login(username='testuser1',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.delete', kwargs={'pk':self.item.pk}), {})
        self.assertEqual(response.status_code, 403)

    def test_call_view_delete_successurl_post(self):
        self.client.login(username='testuser2',
                          password='12345')
        response = self.client.post(reverse('app_name.mymodel.base.delete', kwargs={'pk':self.item.pk}), {})
        self.assertEqual(response.status_code, 302) # redirect

    def test_call_view_list_invalid_post(self):
        self.client.login(username='testuser1',
                          password='12345')
        response = self.client.get(reverse('app_name.mymodel.base.list'), {})
        self.assertEqual(response.status_code, 403)

    def test_call_view_list_successurl_post(self):
        self.client.login(username='testuser2',
                          password='12345')
        response = self.client.get(reverse('app_name.mymodel.base.list'), {})
        self.assertEqual(response.status_code, 200)
