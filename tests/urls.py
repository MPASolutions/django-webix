from django.conf.urls import url, include

from tests.app_name.views import MyLoginView
from tests.app_name.views import MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView
from tests.app_name.views import InlineModelUpdateView
from tests.app_name.views import InlineStackedModelDelete

urlpatterns = [
    url(r'^django-webix/', include('django_webix.urls')),

    url(r'^mylogin$', MyLoginView.as_view(), name='mylogin'),

    url(r'^mymodel/list$', MyModelListView.as_view(), name='mymodel_list'),
    url(r'^mymodel/create$', MyModelCreateView.as_view(), name='mymodel_create'),
    url(r'^mymodel/update/(?P<pk>\d+)$', MyModelUpdateView.as_view(), name='mymodel_update'),
    url(r'^mymodel/delete/(?P<pk>\d+)$', MyModelDeleteView.as_view(), name='mymodel_delete'),

    url(r'^inlinemodel/update/(?P<pk>\d+)$', InlineModelUpdateView.as_view(), name='inlinemodel_update'),

    url(r'^inlinestackedmodel/delete/(?P<pk>\d+)$', InlineStackedModelDelete.as_view(),
        name='inlinestackedmodel_delete'),
]
