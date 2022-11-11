from django.urls import path

from django_webix_filter.views import (DjangoWebixFilterView, FilterConfigView, WebixFilterList, WebixFilterCreate,
                                       WebixFilterUpdate, WebixFilterDelete, FilterSuggestExact)

urlpatterns = [
    path('<str:app_label>/<str:model_name>/', DjangoWebixFilterView.as_view(), name='django_webix.filter.filters'),
    path('<str:app_label>/<str:model_name>/config', FilterConfigView.as_view(),
         name='django_webix.filter.filter_config'),
    path('<str:field>/suggestexact', FilterSuggestExact.as_view(), name='django_webix.filter.suggest_exact'),

    path('webixfilter/create', WebixFilterCreate.as_view(), name='django_webix.filter.webixfilter.create'),
    path('webixfilter/list/<str:app_label>/<str:model_name>', WebixFilterList.as_view(),
         name='django_webix.filter.webixfilter.list_model'),
    path('webixfilter/list', WebixFilterList.as_view(), {'app_label': None, 'model_name': None},
         name='django_webix.filter.webixfilter.list'),
    path('webixfilter/<int:pk>/update', WebixFilterUpdate.as_view(), name='django_webix.filter.webixfilter.update'),
    path('webixfilter/<int:pk>/delete', WebixFilterDelete.as_view(), name='django_webix.filter.webixfilter.delete'),
]
