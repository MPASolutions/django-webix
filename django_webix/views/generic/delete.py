# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView

from django_webix.views.generic.utils import tree_formatter
from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin


class WebixDeleteView(WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin, DeleteView):
    logs_enable = True

    template_name = 'django_webix/generic/delete.js'

    def get_object(self, queryset=None):
        if getattr(self, 'object', None) is not None:
            return self.object
        return super(WebixDeleteView, self).get_object(queryset=queryset)

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.request.method == 'GET':
            if not self.has_view_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_('View permission is not allowed'))
        else:
            if not self.has_delete_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_('Delete permission is not allowed'))
        return super(WebixDeleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixDeleteView, self).get_context_data(**kwargs)
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        # Nested objects
        collector = NestedObjects(using='default')
        collector.collect([self.object])
        context.update({
            'related_objects': json.dumps(tree_formatter(collector.nested())),
        })

        return context

    def get_success_url(self):
        if self.success_url is not None:
            url = self.success_url
        elif self.get_url_list() is not None:
            url = self.get_url_list()
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def get_failure_url(self):
        if self.failure_url:
            url = self.failure_url
        elif self.get_delete(obj=self.object) is not None:
            url = self.get_delete(obj=self.object)
        else:
            raise ImproperlyConfigured(
                "No URL to failure redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def pre_delete_valid(self, **kwargs):
        pass

    def post_delete_valid(self, **kwargs):
        pass

    def response_valid(self, success_url=None, **kwargs):
        return HttpResponseRedirect(success_url)

    def response_invalid(self, failure_url=None, **kwargs):
        return HttpResponseRedirect(failure_url)

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if len(self.get_failure_delete_related_objects(request=request, obj=self.object)) > 0:
            return self.response_invalid(failure_url=self.get_failure_url())

        if self.logs_enable is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, DELETION
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=DELETION
            )

        self.pre_delete_valid()

        success_url = self.get_success_url()
        self.object.delete()

        self.post_delete_valid()

        return self.response_valid(success_url=success_url)
