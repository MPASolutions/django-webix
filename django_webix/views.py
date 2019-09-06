# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

import six
from django.apps import apps
from django.contrib.admin.utils import NestedObjects
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView, ListView, DetailView
from django.views.generic import TemplateView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView

from django_webix.utils import tree_formatter

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver


class WebixPermissionsMixin:
    model = None
    check_permissions = True

    add_permission = None
    change_permission = None
    delete_permission = None
    view_permission = None
    view_or_change_permission = None
    module_permission = None

    enable_button_save_continue = True
    enable_button_save_addanother = True
    enable_button_save_gotolist = True

    _failure_add_related_objects = None
    _failure_change_related_objects = None
    _failure_delete_related_objects = None
    _failure_view_related_objects = None

    def get_failure_add_related_objects(self, request):
        return []

    def get_failure_change_related_objects(self, request, obj=None):
        return []

    def get_failure_delete_related_objects(self, request, obj=None):
        return []

    def get_failure_view_related_objects(self, request, obj=None):
        return []

    def is_enable_button_save_continue(self, request):
        if self.success_url is not None:
            return False
        return self.enable_button_save_continue

    def is_enable_button_save_addanother(self, request):
        if self.success_url is not None:
            return False
        return self.enable_button_save_addanother

    def is_enable_button_save_gotolist(self, request):
        return self.enable_button_save_gotolist

    def has_add_django_user_permission(self, user):
        return user.has_perm('{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_change_django_user_permission(self, user):
        return user.has_perm('{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_delete_django_user_permission(self, user):
        return user.has_perm('{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_view_django_user_permission(self, user):
        return user.has_perm('{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name))

    def has_add_permission(self, request):
        if not self.check_permissions:
            return True
        if self.add_permission is not None:
            return self.add_permission
        if len(self.get_failure_add_related_objects(request)) > 0:
            return False
        return self.has_add_django_user_permission(user=request.user)

    def has_change_permission(self, request, obj=None):
        if not self.check_permissions:
            return True
        if self.change_permission is not None:
            return self.change_permission
        if len(self.get_failure_change_related_objects(request, obj=obj)) > 0:
            return False
        return self.has_change_django_user_permission(user=request.user)

    def has_delete_permission(self, request, obj=None):
        if not self.check_permissions:
            return True
        if self.delete_permission is not None:
            return self.delete_permission
        if len(self.get_failure_delete_related_objects(request, obj=obj)) > 0:
            return False
        return self.has_change_django_user_permission(user=request.user)

    def has_view_permission(self, request, obj=None):
        if not self.check_permissions:
            return True
        if self.view_permission is not None:
            return self.view_permission
        if len(self.get_failure_view_related_objects(request, obj=obj)) > 0:
            return False
        return self.has_view_django_user_permission(user=request.user)

    def has_view_or_change_permission(self, request, obj=None):
        if self.view_permission is not None or self.change_permission is not None:
            return self.view_permission or self.change_permission
        return self.has_view_permission(request=request, obj=obj) or \
               self.has_change_permission(request=request, obj=obj)

    def has_module_permission(self, request):
        if not self.check_permissions:
            return True
        if self.module_permission is not None:
            return self.module_permission
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


class WebixMixinBase(WebixPermissionsMixin, WebixUrlMixin):
    logs_enable = True
    remove_disabled_buttons = False

    def get_container_id(self, request):
        return 'content_right'


class WebixTemplateView(TemplateView):

    def get_container_id(self, request):
        return 'content_right'

    def get_context_data(self, **kwargs):
        context = super(WebixTemplateView, self).get_context_data(**kwargs)
        context.update({
            'webix_container_id': self.get_container_id(request=self.request),
        })
        return context


class WebixCreateView(WebixMixinBase, CreateWithInlinesView):
    style = 'merged'

    def get_template_names(self):
        if self.template_name is None and self.style == 'merged':
            self.template_name = 'django_webix/generic/create.js'
        elif self.template_name is None and self.style == 'unmerged':
            self.template_name = 'django_webix/generic/create_inline_unmerged.js'

        return super(WebixCreateView, self).get_template_names()

    def dispatch(self, *args, **kwargs):
        self.object = None
        if self.request.method == 'GET':
            if not self.has_view_permission(request=self.request):
                raise PermissionDenied(_('View permission is not allowed'))
        else:
            if not self.has_add_permission(request=self.request):
                raise PermissionDenied(_('Add permission is not allowed'))
        return super(WebixCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixCreateView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(request=self.request),
            'has_add_permission': self.has_add_permission(request=self.request),
            'has_change_permission': self.has_change_permission(request=self.request),
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request),
            'has_delete_permission': self.has_delete_permission(request=self.request),
            'has_module_permission': self.has_module_permission(request=self.request),
            'webix_container_id': self.get_container_id(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            'extra_params_url_save': None,
            'extra_path_url_save': None,
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request, obj=self.object),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request, obj=self.object),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request, obj=self.object),
            # buttons for saving
            'is_enable_button_save_continue': self.is_enable_button_save_continue(request=self.request),
            'is_enable_button_save_addanother': self.is_enable_button_save_addanother(request=self.request),
            'is_enable_button_save_gotolist': self.is_enable_button_save_gotolist(request=self.request),
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
        if self.success_url is not None:
            url = self.success_url.format(**self.object.__dict__)

        elif self.request.GET.get('_addanother', None) is not None and \
            self.is_enable_button_save_addanother(request=self.request) and \
            self.get_url_create() is not None:
            url = reverse(self.get_url_create())

        elif self.request.GET.get('_continue', None) is not None and \
            self.is_enable_button_save_continue(request=self.request) and \
            self.get_url_update() is not None:
            url = reverse(self.get_url_update(), kwargs={self.pk_url_kwarg: self.object.pk})

        elif self.get_url_list() is not None and \
            self.is_enable_button_save_gotolist(request=self.request):  # default
            url = reverse(self.get_url_list())

        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def pre_forms_valid(self, form=None, inlines=None, **kwargs):
        pass

    def post_forms_valid(self, form=None, inlines=None, **kwargs):
        anonymous = self.request.user.is_anonymous() if callable(
            self.request.user.is_anonymous) else self.request.user.is_anonymous
        if self.logs_enable is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, ADDITION
            LogEntry.objects.log_action(
                user_id=self.request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=ADDITION
            )

    def response_valid(self, success_url=None, **kwargs):
        return HttpResponseRedirect(success_url)

    def response_invalid(self, form=None, inlines=None, **kwargs):
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))

    def forms_valid(self, form, inlines, **kwargs):
        self.pre_forms_valid(form=form, inlines=inlines, **kwargs)
        self.object = form.save()
        for formset in inlines:
            formset.save()
        self.post_forms_valid(form=form, inlines=inlines, **kwargs)
        return self.response_valid(success_url=self.get_success_url(), **kwargs)

    def forms_invalid(self, form, inlines, **kwargs):
        return self.response_invalid(form=form, inlines=inlines, **kwargs)


class WebixUpdateView(WebixMixinBase, UpdateWithInlinesView):
    style = 'merged'

    def get_template_names(self):
        if self.template_name is None and self.style == 'merged':
            self.template_name = 'django_webix/generic/update.js'
        elif self.template_name is None and self.style == 'unmerged':
            self.template_name = 'django_webix/generic/update_inline_unmerged.js'

        return super(WebixUpdateView, self).get_template_names()

    def get_object(self, queryset=None):
        if getattr(self, 'object', None) is not None:
            return self.object
        return super(WebixUpdateView, self).get_object(queryset=queryset)

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.request.method == 'GET':
            if not self.has_view_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_('View permission is not allowed'))
        else:
            if not self.has_change_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_('Change permission is not allowed'))
        return super(WebixUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixUpdateView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(request=self.request, obj=self.object),
            'has_add_permission': self.has_add_permission(request=self.request),
            'has_change_permission': self.has_change_permission(request=self.request, obj=self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request, obj=self.object),
            'has_delete_permission': self.has_delete_permission(request=self.request, obj=self.object),
            'has_module_permission': self.has_module_permission(request=self.request),
            'webix_container_id': self.get_container_id(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            'extra_params_url_save': None,
            'extra_path_url_save': None,
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request, obj=self.object),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request, obj=self.object),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request, obj=self.object),
            # buttons for saving
            'is_enable_button_save_continue': self.is_enable_button_save_continue(request=self.request),
            'is_enable_button_save_addanother': self.is_enable_button_save_addanother(request=self.request),
            'is_enable_button_save_gotolist': self.is_enable_button_save_gotolist(request=self.request),
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
        if self.success_url is not None:
            url = self.success_url.format(**self.object.__dict__)

        elif self.request.GET.get('_addanother', None) is not None and \
            self.is_enable_button_save_addanother(request=self.request) and \
            self.get_url_create() is not None:
            url = reverse(self.get_url_create())

        elif self.request.GET.get('_continue', None) is not None and \
            self.is_enable_button_save_continue(request=self.request) and \
            self.get_url_update() is not None:
            url = reverse(self.get_url_update(), kwargs={self.pk_url_kwarg: self.object.pk})

        elif self.get_url_list() is not None and \
            self.is_enable_button_save_gotolist(request=self.request):  # default
            url = reverse(self.get_url_list())

        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def pre_forms_valid(self, form=None, inlines=None, **kwargs):
        pass

    def post_forms_valid(self, form=None, inlines=None, **kwargs):
        anonymous = self.request.user.is_anonymous() if callable(
            self.request.user.is_anonymous) else self.request.user.is_anonymous
        if self.logs_enable is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, CHANGE
            LogEntry.objects.log_action(
                user_id=self.request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=CHANGE,
                change_message=_('Changed %s.') % get_text_list(form.changed_data, _('and'))
            )

    def response_valid(self, success_url=None, **kwargs):
        return HttpResponseRedirect(success_url)

    def response_invalid(self, form=None, inlines=None, **kwargs):
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))

    def forms_valid(self, form, inlines, **kwargs):
        self.pre_forms_valid(form=form, inlines=inlines, **kwargs)
        self.object = form.save()
        for formset in inlines:
            formset.save()
        self.post_forms_valid(form=form, inlines=inlines, **kwargs)
        return self.response_valid(success_url=self.get_success_url(), **kwargs)

    def forms_invalid(self, form, inlines, **kwargs):
        return self.response_invalid(form=form, inlines=inlines, **kwargs)


class WebixDeleteView(WebixMixinBase, DeleteView):
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
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(request=self.request, obj=self.object),
            'has_add_permission': self.has_add_permission(request=self.request),
            'has_change_permission': self.has_change_permission(request=self.request, obj=self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request, obj=self.object),
            'has_delete_permission': self.has_delete_permission(request=self.request, obj=self.object),
            'has_module_permission': self.has_module_permission(request=self.request),
            'webix_container_id': self.get_container_id(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            'extra_params_url_save': None,
            'extra_path_url_save': None,
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request, obj=self.object),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request, obj=self.object),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request, obj=self.object),
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(),
            'url_delete': self.get_url_delete(),
            # Model info
            'model': self.model,
            'model_name': self.get_model_name(),
        })

        # Nested objects
        collector = NestedObjects(using='default')
        collector.collect([self.object])
        context.update({
            'related_objects': json.dumps(tree_formatter(collector.nested())),
        })

        return context

    def get_success_url(self):
        if self.success_url is not None:
            url = self.success_url.format(**self.object.__dict__)
        elif self.get_url_list() is not None:
            url = reverse(self.get_url_list())
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def get_failure_url(self):
        if self.failure_url:
            url = self.failure_url.format(**self.object.__dict__)
        elif self.get_failure_url() is not None:
            url = reverse(self.get_failure_url(), kwargs={self.pk_url_kwarg: self.object.pk})
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
        if len(self.get_failure_related_objects()) > 0:
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


class WebixListView(WebixMixinBase, ListView):
    # template_name = 'django_webix/generic/list.js'

    def dispatch(self, *args, **kwargs):
        if not self.has_view_permission(request=self.request):
            raise PermissionDenied(_('View permission is not allowed'))
        return super(WebixListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixListView, self).get_context_data(**kwargs)
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(request=self.request),
            'has_add_permission': self.has_add_permission(request=self.request),
            'has_change_permission': self.has_change_permission(request=self.request),
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request),
            'has_delete_permission': self.has_delete_permission(request=self.request),
            'has_module_permission': self.has_module_permission(request=self.request),
            'webix_container_id': self.get_container_id(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            'extra_params_url_save': None,
            'extra_path_url_save': None,
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request),
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


class WebixDetailView(WebixMixinBase, DetailView):
    # template_name = 'django_webix/generic/detail.js'

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
        context.update({
            # Permissions
            'has_view_permission': self.has_view_permission(request=self.request, obj=self.object),
            'has_add_permission': self.has_add_permission(request=self.request),
            'has_change_permission': self.has_change_permission(request=self.request, obj=self.object),
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request, obj=self.object),
            'has_delete_permission': self.has_delete_permission(request=self.request, obj=self.object),
            'has_module_permission': self.has_module_permission(request=self.request),
            'webix_container_id': self.get_container_id(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            'extra_params_url_save': None,
            'extra_path_url_save': None,
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request),
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
