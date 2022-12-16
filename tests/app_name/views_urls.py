#!/usr/bin/env python

from django_webix.views import (WebixCreateView,
                                WebixUpdateView,
                                WebixDeleteView)
from .models import UrlsModel


class CreateSuccessUrlView(WebixCreateView):
    model = UrlsModel
    fields = '__all__'
    success_url = '/'


class CreateUrlUpdateView(WebixCreateView):
    model = UrlsModel
    fields = '__all__'
    url_update = 'app_name.mymodel.create_urlupdate'


class CreateUrlListView(WebixCreateView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = 'app_name.mymodel.create_urllist'


class CreateNoUrlView(WebixCreateView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = None


class UpdateSuccessUrlView(WebixUpdateView):
    model = UrlsModel
    fields = '__all__'
    success_url = '/'


class UpdateUrlUpdateView(WebixUpdateView):
    model = UrlsModel
    fields = '__all__'
    url_update = 'app_name.mymodel.update_urlupdate'


class UpdateNoUrlView(WebixUpdateView):
    model = UrlsModel
    fields = '__all__'
    url_update = None
    url_list = None


class DeleteSuccessUrlView(WebixDeleteView):
    model = UrlsModel
    success_url = '/'


class DeleteUrlListView(WebixDeleteView):
    model = UrlsModel
    url_list = 'app_name.mymodel.delete_urllist'


class DeleteNoUrlView(WebixDeleteView):
    model = UrlsModel
    url_update = None
    url_list = None
