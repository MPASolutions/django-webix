#!/usr/bin/env python

from django.test import TestCase

class TestFakeLogin(TestCase):

    def setUp(self):
        pass

    def test_login(self):
        response = self.client.get('/mylogin')
        self.assertEqual(response.status_code, 200)
