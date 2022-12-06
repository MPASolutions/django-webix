from django.urls import path

from django_webix.contrib.filter.views import (DjangoWebixFilterView, FilterConfigView, WebixFilterList,
                                               WebixFilterCreate, WebixFilterUpdate, WebixFilterDelete,
                                               FilterSuggestExact)

urlpatterns = [
    path('<str:app_label>/<str:model_name>/', DjangoWebixFilterView.as_view(), name='dwfilter.filters'),
    path('<str:app_label>/<str:model_name>/config', FilterConfigView.as_view(),
         name='dwfilter.filter_config'),
    path('<str:field>/suggestexact', FilterSuggestExact.as_view(), name='dwfilter.suggest_exact'),

    path('webixfilter/create', WebixFilterCreate.as_view(), name='dwfilter.webixfilter.create'),
    path('webixfilter/list/<str:app_label>/<str:model_name>', WebixFilterList.as_view(),
         name='dwfilter.webixfilter.list_model'),
    path('webixfilter/list', WebixFilterList.as_view(), {'app_label': None, 'model_name': None},
         name='dwfilter.webixfilter.list'),
    path('webixfilter/<int:pk>/update', WebixFilterUpdate.as_view(), name='dwfilter.webixfilter.update'),
    path('webixfilter/<int:pk>/delete', WebixFilterDelete.as_view(), name='dwfilter.webixfilter.delete'),
]
