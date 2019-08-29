from django.conf.urls import url, include

from tests.app_name.views import MyLoginView
from tests.app_name.views import MyModelListView, MyModelCreateView, MyModelCreateUnmergedView, \
    MyModelCreateErrorView, MyModelUpdateView, MyModelUpdateErrorView, MyModelDeleteView
from tests.app_name.views import CreateSuccessUrlView, CreateUrlUpdateView, CreateUrlListView, CreateNoUrlView
from tests.app_name.views import UpdateSuccessUrlView, UpdateUrlUpdateView, UpdateNoUrlView
from tests.app_name.views import DeleteSuccessUrlView, DeleteUrlListView, DeleteNoUrlView

from tests.app_name.views import InlineModelUpdateView
from tests.app_name.views import InlineStackedModelDelete

urlpatterns = [
    url(r'^django-webix/', include('django_webix.urls')),

    url(r'^mylogin$', MyLoginView.as_view(), name='mylogin'),

    url(r'^mymodel/list$', MyModelListView.as_view(), name='app_name.mymodel.list'),
    url(r'^mymodel/create$', MyModelCreateView.as_view(), name='app_name.mymodel.create'),
    url(r'^mymodel/create_unmerged$', MyModelCreateUnmergedView.as_view(), name='app_name.mymodel.create_unmerged'),
    url(r'^mymodel/create_error$', MyModelCreateErrorView.as_view(), name='app_name.mymodel.create_error'),
    url(r'^mymodel/update/(?P<pk>\d+)$', MyModelUpdateView.as_view(), name='app_name.mymodel.update'),
    url(r'^mymodel/update_error/(?P<pk>\d+)$', MyModelUpdateErrorView.as_view(), name='app_name.mymodel.update_error'),
    url(r'^mymodel/delete/(?P<pk>\d+)$', MyModelDeleteView.as_view(), name='app_name.mymodel.delete'),

    url(r'^inlinemodel/update/(?P<pk>\d+)$', InlineModelUpdateView.as_view(), name='app_name.inlinemodel.update'),

    url(r'^inlinestackedmodel/delete/(?P<pk>\d+)$', InlineStackedModelDelete.as_view(),
        name='app_name.inlinestackedmodel.delete'),

    url(r'^urlsmodel/create/successurl$', CreateSuccessUrlView.as_view()),
    url(r'^urlsmodel/create/urlcreate$', CreateUrlUpdateView.as_view()),
    url(r'^urlsmodel/create/urllist$', CreateUrlListView.as_view()),
    url(r'^urlsmodel/create/nourl$', CreateNoUrlView.as_view()),

    url(r'^urlsmodel/update/(?P<pk>\d+)/successurl$', UpdateSuccessUrlView.as_view()),
    url(r'^urlsmodel/update/(?P<pk>\d+)/urlcreate$', UpdateUrlUpdateView.as_view()),
    url(r'^urlsmodel/update/(?P<pk>\d+)/nourl$', UpdateNoUrlView.as_view()),

    url(r'^urlsmodel/delete/(?P<pk>\d+)/successurl$', DeleteSuccessUrlView.as_view()),
    url(r'^urlsmodel/delete/(?P<pk>\d+)/urllist$', DeleteUrlListView.as_view()),
    url(r'^urlsmodel/delete/(?P<pk>\d+)/nourl$', DeleteNoUrlView.as_view()),
]
