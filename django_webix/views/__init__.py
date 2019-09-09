from django_webix.views.generic.base import WebixTemplateView
from django_webix.views.generic.detail import WebixDetailView
from django_webix.views.generic.list import WebixListView
from django_webix.views.generic.create_update import (
    WebixCreateView, WebixUpdateView, WebixCreateWithInlinesView, WebixCreateWithInlinesUnmergedView,
    WebixUpdateWithInlinesView, WebixUpdateWithInlinesUnmergedView
)
from django_webix.views.generic.delete import WebixDeleteView

__all__ = [
    'WebixCreateView', 'WebixUpdateView', 'WebixDetailView', 'WebixListView',
    'WebixDeleteView', 'WebixTemplateView',
    # deprecated
    'WebixCreateWithInlinesView', 'WebixCreateWithInlinesUnmergedView', 'WebixUpdateWithInlinesView',
    'WebixUpdateWithInlinesUnmergedView'
]
