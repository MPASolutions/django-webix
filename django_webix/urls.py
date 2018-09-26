# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from django_webix.views_autocomplete import AutocompleteWebixLookup

urlpatterns = [
    url(r'^lookup/autocomplete/$', AutocompleteWebixLookup.as_view(), name="webix_autocomplete_lookup"),
]
