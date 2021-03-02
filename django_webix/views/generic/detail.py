# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.views.generic import DetailView

from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin


class WebixDetailView(WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin, DetailView):
    template_name = 'django_webix/generic/detail.js'

    def get_object(self, queryset=None):
        if getattr(self, 'object', None) is not None:
            return self.object
        return super(WebixDetailView, self).get_object(queryset=queryset)

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if not self.has_view_permission(request=self.request, obj=self.object):
            raise PermissionDenied(_('View permission is not allowed'))
        return super(WebixDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixDetailView, self).get_context_data(**kwargs)
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        return context
