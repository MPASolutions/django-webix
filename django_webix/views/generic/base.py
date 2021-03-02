# -*- coding: utf-8 -*-

from django.apps import apps
from django.conf import settings
from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import BaseFormView


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
            # {
            #     'text': '',
            #     'url': '',
            # },
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
        return self.has_delete_django_user_permission(user=request.user)

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


class WebixUrlUtilsMixin:

    def is_popup(self):
        return self.request.GET.get('_popup', self.request.POST.get('_popup', False)) != False

    def wrap_url_popup(self, url):
        if url is not None:
            if self.is_popup():
                return url + '&_popup' if '?' in url else url + '?_popup'
            else:
                return url
        else:
            return None

    def _check_url(self, url_name, reverse_kwargs=None):
        """
        Check if url_name exists

        :param url_name: url name
        :return: url_name if exists, otherwhise None
        """

        if reverse_kwargs is None:
            reverse_kwargs = {}

        try:
            url = reverse(url_name, kwargs=reverse_kwargs)
            return url_name
        except NoReverseMatch:
            return None


class WebixUrlMixin(WebixUrlUtilsMixin):
    model = None

    url_pattern_list = None
    url_pattern_create = None
    url_pattern_update = None
    url_pattern_delete = None

    def get_url_pattern_list(self):
        if self.url_pattern_list is not None:
            return self.url_pattern_list
        else:
            return '{}.list'.format(self.get_model_name())

    def get_url_pattern_create(self):
        if self.url_pattern_create is not None:
            return self.url_pattern_create
        else:
            return '{}.create'.format(self.get_model_name())

    def get_url_pattern_update(self):
        if self.url_pattern_update is not None:
            return self.url_pattern_update
        else:
            return '{}.update'.format(self.get_model_name())

    def get_url_pattern_delete(self):
        if self.url_pattern_delete is not None:
            return self.url_pattern_delete
        else:
            return '{}.delete'.format(self.get_model_name())

    def get_model_name(self):
        if self.model is not None:
            return '{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name)
        return None

    def get_url_list(self):
        if self.model is not None:
            _url_pattern_name = self._check_url(self.get_url_pattern_list())
            if _url_pattern_name is not None:
                return self.wrap_url_popup(reverse(_url_pattern_name))
        return None

    def get_url_create_kwargs(self):
        return None

    def get_url_create(self):
        if self.model is not None:
            create_kwargs = self.get_url_create_kwargs()
            if create_kwargs is not None:
                _url_pattern_name = self._check_url(self.get_url_pattern_create(),
                                                    reverse_kwargs=self.get_url_create_kwargs())
            else:
                _url_pattern_name = self._check_url(self.get_url_pattern_create())
            if _url_pattern_name is not None:
                if create_kwargs is not None:
                    return self.wrap_url_popup(reverse(_url_pattern_name, kwargs=create_kwargs))
                else:
                    return self.wrap_url_popup(reverse(_url_pattern_name))

        return None

    def get_url_update(self, obj=None):
        if self.model is not None:
            _url_pattern_name = self._check_url(self.get_url_pattern_update(), {'pk': 0})
            if _url_pattern_name is not None:
                if obj is not None:
                    _pk = obj.pk
                else:
                    _pk = 0
                return self.wrap_url_popup(reverse(_url_pattern_name, kwargs={'pk': _pk}))
        return None

    def get_url_delete(self, obj=None):
        if self.model is not None:
            _url_pattern_name = self._check_url(self.get_url_pattern_delete(), {'pk': 0})
            if _url_pattern_name is not None:
                if obj is not None:
                    _pk = obj.pk
                else:
                    _pk = 0
                return self.wrap_url_popup(reverse(_url_pattern_name, kwargs={'pk': _pk}))
        return None

    def get_view_prefix(self):
        return '{}_{}_'.format(self.model._meta.app_label, self.model._meta.model_name)

    def get_context_data_webix_url(self, request, obj=None, **kwargs):
        return {
            # Urls
            'url_list': self.get_url_list(),
            'url_create': self.get_url_create(),
            'url_update': self.get_url_update(obj=obj),
            'url_delete': self.get_url_delete(obj=obj),
            # Model info
            'is_popup': self.is_popup(),
            'model': self.model,
            'model_name': self.get_model_name(),
            'app_label': self.model._meta.app_label if self.model else None,
            'module_name': self.model._meta.model_name if self.model else None,
            'view_prefix': self.get_view_prefix()
        }


class WebixBaseMixin:

    def get_container_id(self, request):
        return settings.WEBIX_CONTAINER_ID

    def get_overlay_container_id(self, request):
        return getattr(settings, 'WEBIX_OVERLAY_CONTAINER_ID', settings.WEBIX_CONTAINER_ID)

    def get_context_data_webix_base(self, request, **kwargs):
        context = {
            'webix_container_id': self.get_container_id(request=self.request),
            'webix_overlay_container_id': self.get_overlay_container_id(request=self.request),
        }
        if hasattr(self, 'model') and self.model is not None:
            context.update({
                'pk_field_name': self.model._meta.pk.name,
            })

        # extra data id django_webix_leaflet is installed
        context.update({
            'layers': self.get_layers(),
        })

        return context

    def get_layers(self):
        layers = []

        if apps.is_installed("qxs") and apps.is_installed("django_webix_leaflet") and getattr(self, 'model',
                                                                                              None) is not None:
            from qxs import qxsreg  # FIXME: add to requirements?

            for model_layer in list(filter(lambda x: x.model == self.model, qxsreg.get_models())):
                layers.append({
                    'codename': model_layer.get_qxs_codename(),
                    'layername': model_layer.get_title(),
                    'qxsname': model_layer.get_qxs_name(),
                    'geofieldname': model_layer.geo_field_name
                })

        return layers


class WebixTemplateView(WebixBaseMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super(WebixTemplateView, self).get_context_data(**kwargs)
        context.update(self.get_context_data_webix_base(request=self.request))
        return context

    def get_view_prefix(self):
        return ''


class WebixFormView(WebixTemplateView, WebixUrlUtilsMixin, BaseFormView):
    """A base view for displaying a form with webix."""

    template_name = 'django_webix/generic/form.js'

    url_pattern_send = None

    def get_url_pattern_send(self):
        if self.url_pattern_send is not None:
            return self.url_pattern_send
        else:
            return resolve(self.request.path_info).url_name

    def get_url_send(self):
        _url_pattern_name = self._check_url(self.get_url_pattern_send())
        if _url_pattern_name is not None:
            return self.wrap_url_popup(reverse(_url_pattern_name))
        return None

    def get_view_prefix(self):
        return self.__module__

    def get_context_data(self, **kwargs):
        context = super(WebixFormView, self).get_context_data(**kwargs)
        context.update({
            # Urls
            'url_send': self.get_url_send(),
            # form view info
            'is_popup': self.is_popup(),
            'view_prefix': self.get_view_prefix()
        })
        return context
