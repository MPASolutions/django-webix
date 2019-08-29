#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from tests.app_name.models import MyModel, InlineModel, InlineStackedModel, UrlsModel


def merge_two_dicts(x, *y):
    z = x.copy()  # start with x's keys and values
    for i in y:
        z.update(i)  # modifies z with y's keys and values & returns None
    return z


class TestFakeLogin(TestCase):
    def test_login(self):
        response = self.client.get('/mylogin')
        self.assertEqual(response.status_code, 200)


class TestUrlsCalls(TestCase):
    def setUp(self):
        self.object = UrlsModel.objects.create(field='Test')

    def test_call_view_create_successurl_post(self):
        response = self.client.post('/urlsmodel/create/successurl', {'field': "Test"})
        self.assertEqual(response.status_code, 302)

    def test_call_view_create_urlcreate_post(self):
        with self.assertRaises(NoReverseMatch):
            self.client.post('/urlsmodel/create/urlcreate', {'field': "Test"})

    def test_call_view_create_urllist_post(self):
        with self.assertRaises(NoReverseMatch):
            self.client.post('/urlsmodel/create/urllist', {'field': "Test"})

    def test_call_view_create_nourl_post(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/urlsmodel/create/nourl', {'field': "Test"})

    def test_call_view_update_successurl_post(self):
        response = self.client.post('/urlsmodel/update/%s/successurl' % self.object.pk, {'field': "Test"})
        self.assertEqual(response.status_code, 302)

    def test_call_view_update_urlcreate_post(self):
        with self.assertRaises(NoReverseMatch):
            self.client.post('/urlsmodel/update/%s/urlcreate' % self.object.pk, {'field': "Test"})

    def test_call_view_update_nourl_post(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/urlsmodel/update/%s/nourl' % self.object.pk, {'field': "Test"})

    def test_call_view_delete_successurl_post(self):
        obj = UrlsModel.objects.create(field='Test')
        response = self.client.post('/urlsmodel/delete/%s/successurl' % obj.pk)
        self.assertEqual(response.status_code, 302)

    def test_call_view_delete_urldelete_post(self):
        obj = UrlsModel.objects.create(field='Test')
        with self.assertRaises(NoReverseMatch):
            self.client.post('/urlsmodel/delete/%s/urllist' % obj.pk)

    def test_call_view_delete_nourl_post(self):
        obj = UrlsModel.objects.create(field='Test')
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/urlsmodel/delete/%s/nourl' % obj.pk)


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

        if not InlineModel.objects.filter(pk=1).exists():
            InlineModel.objects.create(
                id=1,
                inline_field='Test',
                my_model=self.object1
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

    def test_call_view_create_unmerged(self):
        response = self.client.get('/mymodel/create_unmerged')
        self.assertEqual(response.status_code, 200)

    def test_call_view_create_error(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.client.get('/mymodel/create_error')

    def test_call_view_update(self):
        response = self.client.get('/mymodel/update/%s' % self.object1.pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_update_error(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.client.get('/mymodel/update_error/%s' % self.object1.pk)

    def test_call_view_update_inlinemodel(self):
        response = self.client.get('/inlinemodel/update/%s' % self.inlineobject1.pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_delete(self):
        response = self.client.get('/mymodel/delete/%s' % self.object2.pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_delete_stacked(self):
        response = self.client.get('/inlinestackedmodel/delete/%s' % self.object2.inlinestackedmodel_set.first().pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_create_post(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out creation
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
            response = self.client.post('/mymodel/create', dict(self.object_inlines_dict, **self.object_dict))
            self.assertEqual(response.status_code, 302)
            self.client.logout()
        # Verify creation by post
        pk = MyModel.objects.order_by('-id').first().pk
        self.assertEqual(MyModel.objects.get(id=pk).field, 'Test')
        response = self.client.get('/mymodel/update/%s' % pk)
        self.assertEqual(response.status_code, 200)

    def test_call_view_update_post(self):
        for i in ['loggedout', 'loggedin']:  # Logged in and logged out creation
            if i == 'loggedin':
                self.client.login(username='testuser', password='12345')
            response = self.client.post(
                '/mymodel/update/%s' % self.object1.pk,
                merge_two_dicts(self.object_inlines_dict, self.object_dict, {'id': self.object1.pk})
            )
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
            'query_string': 'field=T|field=E:field=T|boolean=TRUE|boolean=FALSE|_to_field=test|field=None'
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
            'model_name': 'inlinestackedmodel',
            'app_label': 'app_name',
            'to_field': 'id',
            'value': 'T'
        })
        self.assertEqual(response.status_code, 200)

    def test_autocomplete_model_foreignkey(self):
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

    def test_autocomplete_error(self):
        self.client.login(username='testuser', password='12345')
        url = "%(url)s?app_label=%(app_label)s&model_name=%(model_name)s&to_field=%(to_field)s&filter[value]=%(value)s"
        response = self.client.get(url % {
            'url': reverse('webix_autocomplete_lookup'),
            'model_name': 'fakemodel',
            'app_label': 'app_name',
            'to_field': 'id',
            'value': 'T'
        })
        self.assertEqual(response.status_code, 200)
