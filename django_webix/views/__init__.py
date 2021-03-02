# -*- coding: utf-8 -*-

from django_webix.views.generic.base import WebixTemplateView, WebixFormView
from django_webix.views.generic.create_update import (
    WebixCreateView, WebixUpdateView
)
from django_webix.views.generic.delete import WebixDeleteView
from django_webix.views.generic.detail import WebixDetailView
from django_webix.views.generic.list import WebixListView, WebixTemplateListView

__all__ = [
    # model views
    'WebixCreateView', 'WebixUpdateView', 'WebixDetailView', 'WebixListView', 'WebixDeleteView',
    # template views
    'WebixTemplateView', 'WebixTemplateListView',
    # form views
    'WebixFormView',
]
