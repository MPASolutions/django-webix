# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import get_text_list
from django.utils.translation import ugettext as _
from extra_views import UpdateWithInlinesView, CreateWithInlinesView

from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin


class WebixCreateUpdateMixin:
    logs_enable = True

    model = None
    request = None

    enable_button_save_continue = True
    enable_button_save_addanother = True
    enable_button_save_gotolist = True

    remove_disabled_buttons = False

    template_style = None

    def get_template_style(self):
        _template_style = None
        if self.template_style is None:
            _template_style = 'standard'
        elif self.template_style in ['standard' or 'tabs']:
            _template_style = self.template_style
        else:
            raise ImproperlyConfigured(
                "Template style is improperly configured"
                " only options are 'standard' or 'tabs'.")
        return _template_style

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

    def get_success_url(self):
        if self.success_url is not None:
            url = self.success_url

        elif self.request.GET.get('_addanother', None) is not None and \
            self.is_enable_button_save_addanother(request=self.request) and \
            self.get_url_create() is not None:
            url = self.get_url_create()

        elif self.request.GET.get('_continue', None) is not None and \
            self.is_enable_button_save_continue(request=self.request) and \
            self.get_url_update(obj=self.object) is not None:
            url = self.get_url_update(obj=self.object)

        elif self.get_url_list() is not None and \
            self.is_enable_button_save_gotolist(request=self.request):  # default
            url = self.get_url_list()

        else:
            raise ImproperlyConfigured(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model.")
        return url

    def validate_unique_together(self, form=None, inlines=None, **kwargs):
        #self.object.validate_unique()
        if form is not None:
            form.instance.validate_unique()


    def get_context_data_webix_create_update(self, request, obj=None, **kwargs):
        return {
            # buttons for saving
            'is_enable_button_save_continue': self.is_enable_button_save_continue(request=self.request),
            'is_enable_button_save_addanother': self.is_enable_button_save_addanother(request=self.request),
            'is_enable_button_save_gotolist': self.is_enable_button_save_gotolist(request=self.request),
            'remove_disabled_buttons': self.remove_disabled_buttons,
            # Template style
            'template_style': self.get_template_style(),
        }


class WebixCreateView(WebixBaseMixin, WebixCreateUpdateMixin, WebixPermissionsMixin, WebixUrlMixin, CreateWithInlinesView):
    template_name = 'django_webix/generic/create.js'

    def get_initial(self):
        initial = {}
        if self.request.GET.get('pk_copy', None) is not None:
            object_to_copy = get_object_or_404(self.get_queryset(), pk=self.request.GET['pk_copy'])
            fields_to_copy = self.form_class._meta.fields
            if self.model._meta.pk.name in fields_to_copy:
                fields_to_copy.remove(self.model._meta.pk.name)
            initial.update(model_to_dict(object_to_copy,
                                         fields=fields_to_copy))
        return initial

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
        context.update(self.get_context_data_webix_permissions(request=self.request))
        context.update(self.get_context_data_webix_create_update(request=self.request))
        context.update(self.get_context_data_webix_url(request=self.request))
        context.update(self.get_context_data_webix_base(request=self.request))
        return context

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
        try:
            self.validate_unique_together(form=form, inlines=inlines, **kwargs)
        except ValidationError as e:
            form.add_error(None,str(e))
            return self.forms_invalid(form=form, inlines=inlines, **kwargs)
        self.object = form.save()
        for formset in inlines:
            formset.save()
        self.post_forms_valid(form=form, inlines=inlines, **kwargs)
        return self.response_valid(success_url=self.get_success_url(), **kwargs)

    def forms_invalid(self, form, inlines, **kwargs):
        return self.response_invalid(form=form, inlines=inlines, **kwargs)


class WebixUpdateView(WebixBaseMixin, WebixCreateUpdateMixin, WebixPermissionsMixin, WebixUrlMixin, UpdateWithInlinesView):
    template_name = 'django_webix/generic/update.js'

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
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_create_update(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        return context

    def validate_unique_together(self, form=None, inlines=None, **kwargs):
        self.object.validate_unique()
        if form is not None:
            form.instance.validate_unique()

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
        try:
            self.validate_unique_together(form=form, inlines=inlines, **kwargs)
        except ValidationError:
            form.add_error(None,str(e))
            return self.forms_invalid(form=form, inlines=inlines, **kwargs)
        self.object = form.save()
        for formset in inlines:
            formset.save()
        self.post_forms_valid(form=form, inlines=inlines, **kwargs)
        return self.response_valid(success_url=self.get_success_url(), **kwargs)

    def forms_invalid(self, form, inlines, **kwargs):
        return self.response_invalid(form=form, inlines=inlines, **kwargs)


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
