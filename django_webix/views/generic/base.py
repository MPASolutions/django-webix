# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import six
from django.conf import settings
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.urls import reverse

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver


class WebixPermissionsMixin:
    model = None
    request = None
    check_permissions = True

    add_permission = None
    change_permission = None
    delete_permission = None
    view_permission = None
    view_or_change_permission = None
    module_permission = None

    _failure_add_related_objects = None
    _failure_change_related_objects = None
    _failure_delete_related_objects = None
    _failure_view_related_objects = None

    remove_disabled_buttons = False

    def get_failure_add_missing_objects(self, request):
        return [
#            {
#                'text': '',
#                'url': '',
#            },
        ]

    def get_failure_add_related_objects(self, request):
        return []

    def get_failure_change_related_objects(self, request, obj=None):
        return []

    def get_failure_delete_related_objects(self, request, obj=None):
        return []

    def get_failure_view_related_objects(self, request, obj=None):
        return []

    def has_add_django_user_permission(self, user):
        if self.model is not None:
            return user.has_perm('{}.add_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        return False

    def has_change_django_user_permission(self, user):
        if self.model is not None:
            return user.has_perm('{}.change_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        return False

    def has_delete_django_user_permission(self, user):
        if self.model is not None:
            return user.has_perm('{}.delete_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        return False

    def has_view_django_user_permission(self, user):
        if self.model is not None:
            return user.has_perm('{}.view_{}'.format(self.model._meta.app_label, self.model._meta.model_name))
        return False

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

    def get_info_no_add_permission(self, has_permission, request):
        if not has_permission:
            return [_("You haven't add permission")]
        return []

    def get_info_no_change_permission(self, has_permission, request, obj=None):
        if not has_permission:
            return [_("You haven't change permission")]
        return []

    def get_info_no_delete_permission(self, has_permission, request, obj=None):
        if not has_permission:
            return [_("You haven't delete permission")]
        return []

    def get_info_no_view_permission(self, has_permission, request, obj=None):
        if not has_permission:
            return [_("You haven't view permission")]
        return []

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
        if self.model is not None:
            return request.user.has_module_perms(self.model._meta.app_label)
        return False

    def get_context_data_webix_permissions(self, request, obj=None, **kwargs):
        _has_view_permission = self.has_view_permission(request=self.request, obj=obj)
        _has_add_permission = self.has_add_permission(request=self.request)
        _has_change_permission = self.has_change_permission(request=self.request, obj=obj)
        _has_delete_permission = self.has_delete_permission(request=self.request, obj=obj)
        return {
            # Buttons
            'remove_disabled_buttons': self.remove_disabled_buttons,
            # Permissions
            'has_view_permission': _has_view_permission,
            'has_add_permission': _has_add_permission,
            'has_change_permission': _has_change_permission,
            'has_delete_permission': _has_delete_permission,
            'has_view_or_change_permission': self.has_view_or_change_permission(request=self.request, obj=obj),
            'has_module_permission': self.has_module_permission(request=self.request),
            # info no permissions
            'info_no_add_permission': self.get_info_no_add_permission(has_permission=_has_add_permission,
                                                                      request=self.request),
            'info_no_change_permission': self.get_info_no_change_permission(has_permission=_has_change_permission,
                                                                            request=self.request,
                                                                            obj=obj),
            'info_no_delete_permission': self.get_info_no_delete_permission(has_permission=_has_delete_permission,
                                                                            request=self.request,
                                                                            obj=obj),
            'info_no_view_permission': self.get_info_no_view_permission(has_permission=_has_view_permission,
                                                                        request=self.request,
                                                                        obj=obj),
            # failure related objects
            'failure_view_related_objects': self.get_failure_view_related_objects(request=self.request,
                                                                                  obj=obj),
            'failure_add_related_objects': self.get_failure_add_related_objects(request=self.request),
            'failure_change_related_objects': self.get_failure_change_related_objects(request=self.request,
                                                                                      obj=obj),
            'failure_delete_related_objects': self.get_failure_delete_related_objects(request=self.request,
                                                                                      obj=obj),
            # filure add missing_objects
            'failure_add_missing_objects': self.get_failure_add_missing_objects(request=self.request),
        }


class WebixUrlMixin:
    model = None

    url_pattern_list = None
    url_pattern_create = None
    url_pattern_update = None
    url_pattern_delete = None

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
        if self.model is not None:
            return '{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name)
        return None

    def get_url_list(self):
        if self.model is not None:
            _url_pattern_name = self.url_pattern_list or self._check_url('{}.list'.format(self.get_model_name()))
            if _url_pattern_name is not None:
                return reverse(_url_pattern_name)
        return None

    def get_url_create_kwargs(self):
        return None

    def get_url_create(self):
        if self.model is not None:
            _url_pattern_name = self.url_pattern_create or self._check_url('{}.create'.format(self.get_model_name()))
            if _url_pattern_name is not None:
                create_kwargs = self.get_url_create_kwargs()
                if create_kwargs is not None:
                    return reverse(_url_pattern_name, kwargs=create_kwargs)
                else:
                    return reverse(_url_pattern_name)
        return None

    def get_url_update(self, obj=None):
        if self.model is not None:
            _url_pattern_name = self.url_pattern_update or self._check_url('{}.update'.format(self.get_model_name()))
            if _url_pattern_name is not None:
                if obj is not None:
                    _pk = obj.pk
                else:
                    _pk = 0
                return reverse(_url_pattern_name, kwargs={'pk': _pk})
        return None

    def get_url_delete(self, obj=None):
        if self.model is not None:
            _url_pattern_name = self.url_pattern_delete or self._check_url('{}.delete'.format(self.get_model_name()))
            if _url_pattern_name is not None:
                if obj is not None:
                    _pk = obj.pk
                else:
                    _pk = 0
                return reverse(_url_pattern_name, kwargs={'pk': _pk})
        return None

    def get_context_data_webix_url(self, request, obj=None, **kwargs):
        return {
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(obj=obj),
            'url_delete': self.get_url_delete(obj=obj),
            # Model info
            'model': self.model,
            'model_name': self.get_model_name(),
        }


class WebixBaseMixin:

    def get_container_id(self, request):
        return settings.WEBIX_CONTAINER_ID

    def get_overlay_container_id(self, request):
        return settings.WEBIX_CONTAINER_ID

    def get_context_data_webix_base(self, request, **kwargs):
        return {
            'webix_container_id': self.get_container_id(request=self.request),
            'webix_overlay_container_id': self.get_overlay_container_id(request=self.request)
        }


class WebixTemplateView(WebixBaseMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(WebixTemplateView, self).get_context_data(**kwargs)
        context.update(self.get_context_data_webix_base(request=self.request))
        return context
