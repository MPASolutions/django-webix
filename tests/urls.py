from django.conf.urls import url, include

from tests.app_name.views import MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView

urlpatterns = [
    url(r'^django-webix/', include('django_webix.urls')),

    url(r'^mymodel/list$', MyModelListView.as_view(), name='mymodel_list'),
    url(r'^mymodel/create$', MyModelCreateView.as_view(), name='mymodel_create'),
    url(r'^mymodel/update/(?P<pk>\d+)$', MyModelUpdateView.as_view(), name='mymodel_update'),
    url(r'^mymodel/delete/(?P<pk>\d+)$', MyModelDeleteView.as_view(), name='mymodel_delete'),
]
