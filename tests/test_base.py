#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from tests.app_name.models import MyModel, InlineModel, InlineStackedModel


class TestCalls(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.object_dict = {
            'field': 'Test',
            'email': 'test@test.com',
            'floatfield': 2.6,
            'decimalfield': 8.1,
            'integerfield': 1
        }

        self.object1 = MyModel.objects.create(**self.object_dict)
        self.object2 = MyModel.objects.create(**self.object_dict)
        self.inlineobject1 = InlineModel.objects.create(
            inline_field='Test',
            my_model=self.object1
        )
        self.inlineobject2 = InlineModel.objects.create(
            inline_field='Test',
            my_model=self.object2
        )

        for i in range(100):
            InlineStackedModel.objects.create(
                my_model=self.object2
            )

        self.object_inlines_dict = {
            'inlinemodel_set-TOTAL_FORMS': 3,
            'inlinemodel_set-INITIAL_FORMS': 0,
            'inlinemodel_set-MIN_NUM_FORMS': 0,
            'inlinemodel_set-MAX_NUM_FORMS': 1000,
            'inlinestackedmodel_set-0-booleanfield': '2',
            'inlinestackedmodel_set-0-inlinemodels': '%s,%s' % (self.inlineobject1.pk, self.inlineobject2.pk),
            'inlinestackedmodel_set-1-booleanfield': '2',
            'inlinestackedmodel_set-1-inlinemodels': '',
            'inlinestackedmodel_set-TOTAL_FORMS': 3,
            'inlinestackedmodel_set-INITIAL_FORMS': 0,
            'inlinestackedmodel_set-MIN_NUM_FORMS': 0,
            'inlinestackedmodel_set-MAX_NUM_FORMS': 1000,
            'inlineemptymodel_set-TOTAL_FORMS': 3,
            'inlineemptymodel_set-INITIAL_FORMS': 0,
            'inlineemptymodel_set-MIN_NUM_FORMS': 0,
            'inlineemptymodel_set-MAX_NUM_FORMS': 1000
        }

    def test_call_view_list(self):
        response = self.client.get('/mymodel/list')
        self.assertEqual(response.status_code, 200)

    def test_call_view_create(self):
        response = self.client.get('/mymodel/create')
        self.assertEqual(response.status_code, 200)

    def test_call_view_update(self):
        response = self.client.get('/mymodel/update/%s' % self.object1.pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_delete(self):
        response = self.client.get('/mymodel/delete/%s' % self.object2.pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_create_post(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out creation
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
            response = self.client.post('/mymodel/create', dict(self.object_inlines_dict, **self.object_dict))
            self.assertEqual(response.status_code, 302)
            self.client.logout()
        # Verify creation by post
        self.assertEqual(MyModel.objects.get(id=2).field, 'Test')
        response = self.client.get('/mymodel/update/%s' % 2)
        self.assertEqual(response.status_code, 200)

    def test_call_view_update_post(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out update
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
            response = self.client.post('/mymodel/update/%s' % self.object1.pk, dict(
                self.object_inlines_dict, **self.object_dict
            ))
            self.assertEqual(response.status_code, 302)
            self.client.logout()
        # Verify creation by post
        self.assertEqual(MyModel.objects.get(id=self.object1.pk).field, 'Test')

    def test_call_view_errors_update_post(self):
        self.client.login(username='testuser', password='12345')
        with self.assertRaises(ValidationError):
            self.client.post('/mymodel/update/%s' % self.object1.pk, {
                'inlinestackedmodel_set-INITIAL_FORMS': 3,
                'inlinestackedmodel_set-MIN_NUM_FORMS': 1,
                'inlinestackedmodel_set-MAX_NUM_FORMS': 1000
            })
        # self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_call_view_delete_post(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out update
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
                response = self.client.post('/mymodel/delete/%s' % self.object2.pk, {})
            else:
                response = self.client.post('/mymodel/delete/%s' % self.object1.pk, {})
            self.assertEqual(response.status_code, 302)
            self.client.logout()

    def test_autocomplete_logged_querysetring(self):
        self.client.login(username='testuser', password='12345')
        url = "%(url)s?app_label=%(app_label)s&model_name=%(model_name)s&to_field=%(to_field)s&" \
              "filter[value]=%(value)s&query_string=%(query_string)s"
        response = self.client.get(url % {
            'url': reverse('webix_autocomplete_lookup'),
            'model_name': 'mymodel',
            'app_label': 'app_name',
            'to_field': 'id',
            'value': 'T',
            'query_string': 'field=T|field=E:field=T|boolean=TRUE|boolean=FALSE|_to_field=test'
        })
        self.assertEqual(response.status_code, 200)

    def test_autocomplete_without_querysetring(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out update
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
            url = "%(url)s?app_label=%(app_label)s&model_name=%(model_name)s&to_field=%(to_field)s&" \
                  "filter[value]=%(value)s&nolimit=True"
            response = self.client.get(url % {
                'url': reverse('webix_autocomplete_lookup'),
                'model_name': 'mymodel',
                'app_label': 'app_name',
                'to_field': 'id',
                'value': 'T'
            })
            if i == 'loggedout':
                self.assertEqual(response.status_code, 403)
            else:
                self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_autocomplete_model_without_autocomplete(self):
        self.client.login(username='testuser', password='12345')
        url = "%(url)s?app_label=%(app_label)s&model_name=%(model_name)s&to_field=%(to_field)s&filter[value]=%(value)s"
        response = self.client.get(url % {
            'url': reverse('webix_autocomplete_lookup'),
            'model_name': 'inlinemodel',
            'app_label': 'app_name',
            'to_field': 'id',
            'value': 'T'
        })
        self.assertEqual(response.status_code, 200)

    def test_autocomplete_invalid(self):
        self.client.login(username='testuser', password='12345')
        url = "%(url)s?app_label=%(app_label)s&to_field=%(to_field)s&filter[value]=%(value)s"
        response = self.client.get(url % {
            'url': reverse('webix_autocomplete_lookup'),
            'app_label': 'app_name',
            'to_field': 'id',
            'value': 'T'
        })
        self.assertEqual(response.status_code, 200)


class TestGenericModelWebix(TestCase):
    def setUp(self):
        self.object = MyModel.objects.create(**{
            'field': 'Test',
            'email': 'test@test.com',
            'floatfield': 2.6,
            'decimalfield': 8.1,
            'integerfield': 1
        })
        self.object_inline = InlineModel.objects.create(
            inline_field='Text',
            my_model=self.object
        )

    def test_get_url_name(self):
        self.assertEqual(self.object.get_url_list, 'mymodel_list')
        self.assertEqual(self.object.get_url_create, 'mymodel_create')
        self.assertEqual(self.object.get_url_update, 'mymodel_update')
        self.assertEqual(self.object.get_url_delete, 'mymodel_delete')
        self.assertEqual(self.object_inline.get_url_list, None)
        self.assertEqual(self.object_inline.get_url_create, None)
        self.assertEqual(self.object_inline.get_url_update, None)
        self.assertEqual(self.object_inline.get_url_delete, None)

    def test_get_model_name(self):
        self.assertEqual(self.object.get_model_name, 'app_name_mymodel')
        self.assertEqual(self.object_inline.get_model_name, 'app_name_inlinemodel')
