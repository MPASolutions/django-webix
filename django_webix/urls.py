# -*- coding: utf-8 -*-

from django.conf.urls import url

from django_webix.views.views_autocomplete import AutocompleteWebixLookup
from django_webix.views.views_user_agent_limit import UserAgentLimit

urlpatterns = [
    url(r'^lookup/autocomplete/$', AutocompleteWebixLookup.as_view(), name="webix_autocomplete_lookup"),
    url(r'^user_agent/limit/$', UserAgentLimit.as_view(), name="webix_user_agent_limit"),
]
