# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.forms import all_valid
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView


class WebixPermissionsMixin:
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj) or self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        return True


class WebixCreateWithInlinesView(WebixPermissionsMixin, CreateWithInlinesView):
    template_name = 'django_webix/generic/create.js'

    def get_context_data(self, **kwargs):
        context = super(WebixCreateWithInlinesView, self).get_context_data(**kwargs)
        context.update({
            'has_add_permission': self.has_add_permission(self.request),
            'has_module_permission': self.has_module_permission(self.request)
        })
        return context

    def get_success_url(self):
        if hasattr(self.object, 'WebixMeta') and hasattr(self.object.WebixMeta, 'url_update'):
            return reverse(self.object.WebixMeta.url_update, kwargs={"pk": self.object.pk})
        elif hasattr(self.object, 'WebixMeta') and hasattr(self.object.WebixMeta, 'url_list'):
            return reverse(self.object.WebixMeta.url_list)
        return super(WebixCreateWithInlinesView, self).get_success_url()

    def post(self, request, *args, **kwargs):
        response = super(WebixCreateWithInlinesView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if all_valid(inlines) and form.is_valid() and not anonymous:
            from django.contrib.admin.models import LogEntry, ADDITION
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=ADDITION
            )

        return response


class WebixCreateWithInlinesUnmergedView(WebixCreateWithInlinesView):
    template_name = 'django_webix/generic/create_inline_unmerged.js'


class WebixUpdateWithInlinesView(WebixPermissionsMixin, UpdateWithInlinesView):
    template_name = 'django_webix/generic/update.js'

    def get_context_data(self, **kwargs):
        context = super(WebixUpdateWithInlinesView, self).get_context_data(**kwargs)
        context.update({
            'has_view_permission': self.has_view_permission(self.request, self.object),
            'has_change_permission': self.has_change_permission(self.request, self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(self.request, self.object),
            'has_delete_permission': self.has_delete_permission(self.request, self.object),
            'has_module_permission': self.has_module_permission(self.request)
        })
        return context

    def get_success_url(self):
        if hasattr(self.object, 'WebixMeta') and hasattr(self.object.WebixMeta, 'url_update'):
            return reverse(self.object.WebixMeta.url_update, kwargs={"pk": self.object.pk})
        return super(WebixUpdateWithInlinesView, self).get_success_url()

    def post(self, request, *args, **kwargs):
        response = super(WebixUpdateWithInlinesView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if all_valid(inlines) and form.is_valid() and not anonymous:
            from django.contrib.admin.models import LogEntry, CHANGE
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=CHANGE,
                change_message=_('Changed %s.') % get_text_list(form.changed_data, _('and'))
            )

        return response


class WebixUpdateWithInlinesUnmergedView(WebixUpdateWithInlinesView):
    template_name = 'django_webix/generic/update_inline_unmerged.js'


class WebixDeleteView(WebixPermissionsMixin, DeleteView):
    template_name = 'django_webix/generic/delete.js'
    nested_prevent = False

    def _as_webix_tree(self, obj):
        if isinstance(obj, list) and len(obj) == 2:
            item = '{}: {}'.format(capfirst(obj[0]._meta.verbose_name), force_text(obj[0]))
            _data = {"value": item, "open": True}
            if hasattr(obj[0], 'WebixMeta') and hasattr(obj[0].WebixMeta, 'url_update'):
                _data.update({'url': reverse(obj[0].WebixMeta.url_update, kwargs={"pk": obj[0].pk})})
            _data.update({"data": self._as_webix_tree(obj[1])})
            return [_data]
        elif isinstance(obj, list):
            _data = []
            for item in obj:
                _item = {"value": '{}: {}'.format(capfirst(item._meta.verbose_name), force_text(item))}
                if hasattr(item, 'WebixMeta') and hasattr(item.WebixMeta, 'url_update'):
                    _item.update({'url': reverse(item.WebixMeta.url_update, kwargs={"pk": item.pk})})
                _data.append(_item)
            return _data
        else:
            return []

    def get_context_data(self, **kwargs):
        context = super(WebixDeleteView, self).get_context_data(**kwargs)
        context.update({
            'has_view_permission': self.has_view_permission(self.request, self.object),
            'has_delete_permission': self.has_delete_permission(self.request, self.object),
            'has_module_permission': self.has_module_permission(self.request)
        })

        # Nested objects
        collector = NestedObjects(using='default')
        collector.collect([self.object])
        context.update({
            'related': json.dumps(self._as_webix_tree(collector.nested())),
            'nested_prevent': False if self.nested_prevent and len(collector.data) <= 1 else self.nested_prevent
        })

        return context

    def get_success_url(self):
        if hasattr(self.object, 'WebixMeta') and hasattr(self.object.WebixMeta, 'url_list'):
            return reverse(self.object.WebixMeta.url_list)
        return super(WebixDeleteView, self).get_success_url()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if not anonymous:
            from django.contrib.admin.models import LogEntry, DELETION
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=DELETION
            )

        return super(WebixDeleteView, self).delete(request, *args, **kwargs)
