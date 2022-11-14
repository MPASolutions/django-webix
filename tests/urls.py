from django.urls import path, include

from django_webix.contrib.admin import site
from tests.app_name.views import (MyLoginView,
                                  MyModelCreateBaseView,
                                  MyModelUpdateBaseView,
                                  MyModelDeleteBaseView,
                                  MyModelListBaseView)
from tests.app_name.views import (MyModelListView,
                                  MyModelCreateView,
                                  MyModelCreateErrorView,
                                  MyModelUpdateView,
                                  MyModelUpdateErrorView,
                                  MyModelDeleteView)
from tests.app_name.views_urls import (CreateSuccessUrlView, CreateUrlUpdateView, CreateUrlListView, CreateNoUrlView,
                                       UpdateSuccessUrlView, UpdateUrlUpdateView, UpdateNoUrlView,
                                       DeleteSuccessUrlView, DeleteUrlListView, DeleteNoUrlView)

urlpatterns = [

    path('django-webix/', include('django_webix.urls')),
    path('main/', site.urls),
    path('django_webix/auth/', include('django_webix.contrib.auth.urls')),

    path('mylogin', MyLoginView.as_view(), name='mylogin'),

    path('mymodel/base/create', MyModelCreateBaseView.as_view(), name='app_name.mymodel.base.create'),
    path('mymodel/base/update/<int:pk>', MyModelUpdateBaseView.as_view(), name='app_name.mymodel.base.update'),
    path('mymodel/base/delete/<int:pk>', MyModelDeleteBaseView.as_view(), name='app_name.mymodel.base.delete'),
    path('mymodel/base/list', MyModelListBaseView.as_view(), name='app_name.mymodel.base.list'),

    path('mymodel/list', MyModelListView.as_view(), name='app_name.mymodel.list'),
    path('mymodel/create', MyModelCreateView.as_view(), name='app_name.mymodel.create'),
    path('mymodel/create_error', MyModelCreateErrorView.as_view(), name='app_name.mymodel.create_error'),
    path('mymodel/update/<int:pk>', MyModelUpdateView.as_view(), name='app_name.mymodel.update'),
    path('mymodel/update_error/<int:pk>', MyModelUpdateErrorView.as_view(), name='app_name.mymodel.update_error'),
    path('mymodel/delete/<int:pk>', MyModelDeleteView.as_view(), name='app_name.mymodel.delete'),

    path('urlsmodel/create/successurl', CreateSuccessUrlView.as_view()),
    path('urlsmodel/create/urlcreate', CreateUrlUpdateView.as_view()),
    path('urlsmodel/create/urllist', CreateUrlListView.as_view()),
    path('urlsmodel/create/nourl', CreateNoUrlView.as_view()),

    path('urlsmodel/update/<int:pk>/successurl', UpdateSuccessUrlView.as_view()),
    path('urlsmodel/update/<int:pk>/urlcreate', UpdateUrlUpdateView.as_view()),
    path('urlsmodel/update/<int:pk>/nourl', UpdateNoUrlView.as_view()),

    path('urlsmodel/delete/<int:pk>/successurl', DeleteSuccessUrlView.as_view()),
    path('urlsmodel/delete/<int:pk>/urllist', DeleteUrlListView.as_view()),
    path('urlsmodel/delete/<int:pk>/nourl', DeleteNoUrlView.as_view()),
]
