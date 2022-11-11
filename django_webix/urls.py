
from django.urls import path

from django_webix.views.views_autocomplete import AutocompleteWebixLookup
from django_webix.views.views_user_agent_limit import UserAgentLimit

urlpatterns = [
    path('lookup/autocomplete/', AutocompleteWebixLookup.as_view(), name="webix_autocomplete_lookup"),
    path('user_agent/limit/', UserAgentLimit.as_view(), name="webix_user_agent_limit"),
]
