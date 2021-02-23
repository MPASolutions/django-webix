from django_webix.views.generic.base import WebixTemplateView, WebixFormView
from django_webix.views.generic.detail import WebixDetailView
from django_webix.views.generic.list import WebixListView, WebixTemplateListView
from django_webix.views.generic.create_update import (
    WebixCreateView, WebixUpdateView, WebixCreateWithInlinesView, WebixCreateWithInlinesUnmergedView,
    WebixUpdateWithInlinesView, WebixUpdateWithInlinesUnmergedView
)
from django_webix.views.generic.delete import WebixDeleteView

__all__ = [
    # model views
    'WebixCreateView', 'WebixUpdateView', 'WebixDetailView', 'WebixListView', 'WebixDeleteView',
    # template views
    'WebixTemplateView', 'WebixTemplateListView',
    # form views
    'WebixFormView',
    # deprecated
    'WebixCreateWithInlinesView', 'WebixCreateWithInlinesUnmergedView', 'WebixUpdateWithInlinesView',
    'WebixUpdateWithInlinesUnmergedView'
]
