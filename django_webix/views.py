# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import six
from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.forms import all_valid
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver

from django_webix.utils import tree_formatter


class WebixPermissionsMixin:
    model = None
    permissions = True

    def has_add_permission(self, request):
        if not self.permissions:
            return True
        return request.user.has_perm('{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_change_permission(self, request, obj=None):
        if not self.permissions:
            return True
        return request.user.has_perm('{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_delete_permission(self, request, obj=None):
        if not self.permissions:
            return True
        return request.user.has_perm('{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_view_permission(self, request, obj=None):
        if not self.permissions:
            return True
        return request.user.has_perm('{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_view_permission(request, obj) or self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        if not self.permissions:
            return True
        return request.user.has_module_perms(self.model._meta.app_label)


class WebixUrlMixin:
    model = None

    url_list = None
    url_create = None
    url_update = None
    url_delete = None

    def _check_url(self, url_name):
        """
        Check if url_name exists

        :param url_name: url name
        :return: url_name if exists, otherwhise None
        """

        exists = url_name in [i for i in get_resolver(None).reverse_dict.keys() if isinstance(i, six.string_types)]
        if exists:
            return url_name
        return None

    def get_model_name(self):
        return '{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name)

    def get_url_list(self):
        return self.url_list or self._check_url('{}.list'.format(self.get_model_name()))

    def get_url_create(self):
        return self.url_create or self._check_url('{}.create'.format(self.get_model_name()))

    def get_url_update(self):
        return self.url_update or self._check_url('{}.update'.format(self.get_model_name()))

    def get_url_delete(self):
        return self.url_delete or self._check_url('{}.delete'.format(self.get_model_name()))


class WebixCreateView(WebixPermissionsMixin, WebixUrlMixin, CreateWithInlinesView):
    logs = True
    style = 'merged'

    def get_template_names(self):
        if self.template_name is None and self.style == 'merged':
            self.template_name = 'django_webix/generic/create.js'
        elif self.template_name is None and self.style == 'unmerged':
            self.template_name = 'django_webix/generic/create_inline_unmerged.js'

        return super(WebixCreateView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(WebixCreateView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(self.request),
            'has_add_permission': self.has_add_permission(self.request),
            'has_change_permission': self.has_change_permission(self.request),
            'has_view_or_change_permission': self.has_view_or_change_permission(self.request),
            'has_delete_permission': self.has_delete_permission(self.request),
            'has_module_permission': self.has_module_permission(self.request),
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(),
            'url_delete': self.get_url_delete(),
            # Model info
            'model': self.model,
            'model_name': self.get_model_name()
        })
        return context

    def get_success_url(self):
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        elif self.get_url_update() is not None:
            url = reverse(self.get_url_update(), kwargs={self.pk_url_kwarg: self.object.pk})
        elif self.get_url_list() is not None:
            url = reverse(self.get_url_list())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def post(self, request, *args, **kwargs):
        response = super(WebixCreateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if self.logs is True and not anonymous and apps.is_installed('django.contrib.admin') and \
            all_valid(inlines) and form.is_valid():
            from django.contrib.admin.models import LogEntry, ADDITION
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=ADDITION
            )

        return response


class WebixUpdateView(WebixPermissionsMixin, WebixUrlMixin, UpdateWithInlinesView):
    logs = True
    style = 'merged'

    def get_template_names(self):
        if self.template_name is None and self.style == 'merged':
            self.template_name = 'django_webix/generic/update.js'
        elif self.template_name is None and self.style == 'unmerged':
            self.template_name = 'django_webix/generic/update_inline_unmerged.js'

        return super(WebixUpdateView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(WebixUpdateView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(self.request, self.object),
            'has_add_permission': self.has_add_permission(self.request),
            'has_change_permission': self.has_change_permission(self.request, self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(self.request, self.object),
            'has_delete_permission': self.has_delete_permission(self.request, self.object),
            'has_module_permission': self.has_module_permission(self.request),
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(),
            'url_delete': self.get_url_delete(),
            # Model info
            'model': self.model,
            'model_name': self.get_model_name()
        })
        return context

    def get_success_url(self):
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        elif self.get_url_update() is not None:
            url = reverse(self.get_url_update(), kwargs={self.pk_url_kwarg: self.object.pk})
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def post(self, request, *args, **kwargs):
        response = super(WebixUpdateView, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        inlines = self.construct_inlines()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if self.logs is True and not anonymous and apps.is_installed('django.contrib.admin') \
            and all_valid(inlines) and form.is_valid():
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


class WebixDeleteView(WebixPermissionsMixin, WebixUrlMixin, DeleteView):
    logs = True
    template_name = 'django_webix/generic/delete.js'
    nested_prevent = False

    def get_context_data(self, **kwargs):
        context = super(WebixDeleteView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(self.request, self.object),
            'has_change_permission': self.has_change_permission(self.request, self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(self.request, self.object),
            'has_delete_permission': self.has_delete_permission(self.request, self.object),
            'has_module_permission': self.has_module_permission(self.request),
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(),
            'url_delete': self.get_url_delete(),
            # Model info
            'model': self.model,
            'model_name': self.get_model_name()
        })

        # Nested objects
        collector = NestedObjects(using='default')
        collector.collect([self.object])
        context.update({
            'related': json.dumps(tree_formatter(collector.nested())),
            'nested_prevent': False if self.nested_prevent and len(collector.data) <= 1 else self.nested_prevent
        })

        return context

    def get_success_url(self):
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        elif self.get_url_list() is not None:
            url = reverse(self.get_url_list())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if self.logs is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, DELETION
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=DELETION
            )

        return super(WebixDeleteView, self).delete(request, *args, **kwargs)


class WebixCreateWithInlinesView(WebixCreateView):
    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn('`django_webix.views.WebixCreateWithInlinesView` has been renamed to `WebixCreateView`. '
             '`WebixCreateWithInlinesView` will be removed in a future release.', DeprecationWarning)
        super(WebixCreateWithInlinesView, self).__init__(*args, **kwargs)


class WebixCreateWithInlinesUnmergedView(WebixCreateView):
    style = 'unmerged'

    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn('`django_webix.views.WebixCreateWithInlinesUnmergedView` has been renamed to `WebixCreateView`. '
             '`WebixCreateWithInlinesUnmergedView` will be removed in a future release.', DeprecationWarning)
        super(WebixCreateWithInlinesUnmergedView, self).__init__(*args, **kwargs)


class WebixUpdateWithInlinesView(WebixUpdateView):
    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn('`django_webix.views.WebixUpdateWithInlinesView` has been renamed to `WebixUpdateView`. '
             '`WebixUpdateWithInlinesView` will be removed in a future release.', DeprecationWarning)
        super(WebixUpdateWithInlinesView, self).__init__(*args, **kwargs)


class WebixUpdateWithInlinesUnmergedView(WebixUpdateView):
    style = 'unmerged'

    def __init__(self, *args, **kwargs):
        from warnings import warn
        warn('`django_webix.views.WebixUpdateWithInlinesUnmergedView` has been renamed to `WebixUpdateView`. '
             '`WebixUpdateWithInlinesUnmergedView` will be removed in a future release.', DeprecationWarning)
        super(WebixUpdateWithInlinesUnmergedView, self).__init__(*args, **kwargs)
