# -*- coding: utf-8 -*-

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.forms.fields import FileField
from django.forms.formsets import all_valid
from django.forms.models import _get_foreign_key, ModelForm, fields_for_model
from django.http import HttpResponseRedirect
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_text
from django.utils.text import get_text_list
from django.utils.translation import gettext as _
from extra_views import UpdateWithInlinesView, CreateWithInlinesView
from sorl.thumbnail.fields import ImageField

from django_webix.forms import WebixModelForm
from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin
from django_webix.views.generic.signals import (django_webix_view_pre_save,
                                                django_webix_view_pre_inline_save,
                                                django_webix_view_post_save)


class WebixCreateUpdateMixin:
    logs_enable = True

    model = None
    request = None

    enable_button_save_continue = True
    enable_button_save_addanother = True
    enable_button_save_gotolist = True

    template_style = None

    def get_form_class(self):
        """Return the form class to use."""

        form_class = super().get_form_class()

        # Transform ModelForm into WebixModelForm
        if not isinstance(form_class, WebixModelForm) and issubclass(form_class, ModelForm):
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif getattr(self, 'object', None) is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            form_class.__bases__ = (WebixModelForm,)
            form_class = type(str(model.__name__ + 'Form'), (form_class,), {})

        return form_class

    def get_template_style(self):
        _template_style = None
        if self.template_style is None:
            _template_style = 'standard'
        elif self.template_style in ['standard', 'tabs']:
            _template_style = self.template_style
        else:
            raise ImproperlyConfigured(_(
                "Template style is improperly configured"
                " only options are 'standard' or 'tabs' (standard by default)."))
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
            raise ImproperlyConfigured(_(
                "No URL to redirect to.  Either provide a url or define"
                " a get_absolute_url method on the Model."))
        return url

    def get_context_data_webix_create_update(self, request, obj=None, **kwargs):

        return {
            # buttons for saving
            'is_enable_button_save_continue': self.is_enable_button_save_continue(request=self.request),
            'is_enable_button_save_addanother': self.is_enable_button_save_addanother(request=self.request),
            'is_enable_button_save_gotolist': self.is_enable_button_save_gotolist(request=self.request),
            # Template style
            'template_style': self.get_template_style(),
        }

    def form_save(self, form):
        obj = form.instance
        if obj is not None:
            for field in obj._meta.fields:
                if not isinstance(field, FileField) and not isinstance(field, ImageField):
                    continue

                if form.data.get(field.name + '_clean', None) == '1':
                    setattr(obj, field.name, None)

        self.object = form.save()
        return None

    def inlines_save(self, inlines):
        for formset in inlines:
            for inline in formset:
                obj = inline.instance
                if obj is not None:
                    for field in obj._meta.fields:
                        if not isinstance(field, FileField) and not isinstance(field, ImageField):
                            continue

                        if inline.data.get(inline.add_prefix(field.name) + '_clean', None) == '1':
                            setattr(obj, field.name, None)
                            inline.save()

            formset.save()
        return None

    def forms_valid(self, form, inlines, **kwargs):
        # pre forms valid
        self.pre_forms_valid(form=form, inlines=inlines, **kwargs)
        # validate unique together
        try:
            self.validate_unique_together(form=form, inlines=inlines, **kwargs)
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.forms_invalid(form=form, inlines=inlines, **kwargs)
        # form save
        exception_response = self.form_save(form)
        if exception_response is not None:
            return exception_response
        # post form save
        self.post_form_save(form=form, inlines=inlines, **kwargs)
        # inlines save
        exception_response = self.inlines_save(inlines)
        if exception_response is not None:
            return exception_response
        # post forms valid
        self.post_forms_valid(form=form, inlines=inlines, **kwargs)

        return self.response_valid(success_url=self.get_success_url(), **kwargs)

    def full_validate(self, form, form_validated, inlines, inlines_validated):
        return form, inlines, form_validated and inlines_validated

    def validate_form(self, form):
        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False
        return form, form_validated

    def validate_inlines(self, inlines):
        inlines_validated = all_valid(inlines)
        return inlines, inlines_validated

    def response_valid(self, success_url=None, **kwargs):
        return HttpResponseRedirect(success_url)

    def response_invalid(self, form=None, inlines=None, **kwargs):
        return self.render_to_response(self.get_context_data(form=form, inlines=inlines))

    def forms_invalid(self, form, inlines, **kwargs):
        return self.response_invalid(form=form, inlines=inlines, **kwargs)


class WebixCreateView(WebixCreateUpdateMixin,
                      WebixBaseMixin,
                      WebixPermissionsMixin,
                      WebixUrlMixin,
                      CreateWithInlinesView):
    template_name = 'django_webix/generic/create.js'
    model_copy_fields = None
    inlines_copy_fields = None
    send_initial_data = None

    def construct_inlines(self):
        """
        Returns the inline formset instances
        """
        inline_formsets = []
        initial_inlines = self.get_initial_inlines()
        for inline_class in self.get_inlines():
            kwargs = self.kwargs
            initial = initial_inlines.get(inline_class, None)
            inline_instance = inline_class(self.model, self.request, self.object, kwargs, self, initial)
            inline_formset = inline_instance.construct_formset()
            inline_formsets.append(inline_formset)
        return inline_formsets

    def get_form_kwargs(self):
        kwargs = super(WebixCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_model_copy_fields(self):
        if self.model_copy_fields is None:
            form_class = self.get_form_class()
            _model_copy_fields = form_class._meta.fields
            if _model_copy_fields is None:  # __all__ option
                opts = form_class._meta
                _model_copy_fields = list(fields_for_model(
                    opts.model, opts.fields, opts.exclude, opts.widgets,
                    getattr(opts, 'formfield_callback', None), opts.localized_fields, opts.labels,
                    opts.help_texts, opts.error_messages, opts.field_classes,
                    # limit_choices_to will be applied during ModelForm.__init__().
                    apply_limit_choices_to=False,
                ).keys())
        else:
            _model_copy_fields = self.model_copy_fields
        return _model_copy_fields

    def get_inlines_copy_fields(self):

        # init
        _inlines_copy_fields = {}
        if self.inlines_copy_fields is None:
            for inline in self.get_inlines():
                _inlines_copy_fields.update({inline: None})
        else:
            _inlines_copy_fields = self.inlines_copy_fields

        full_inlines_copy_fields = {}
        # set fields for each inlines
        for inline, fields in _inlines_copy_fields.items():
            if fields is None:
                fields = []
            full_inlines_copy_fields.update({inline: list(inline.form_class.base_fields.keys())})

        return full_inlines_copy_fields

    def get_initial(self):
        initial = {}
        # main option: send SEND_INITIAL_DATA on (header or GET or POST) and POST initial data
        if self.send_initial_data is not None:
            initial.update(self.send_initial_data)
        # secondary option: send pk_copy for copy instance field values
        elif self.request.GET.get('pk_copy', None) is not None:
            object_to_copy = get_object_or_404(self.get_queryset(), pk=self.request.GET['pk_copy'])
            fields_to_copy = self.get_model_copy_fields()
            if self.model._meta.pk.name in fields_to_copy:
                fields_to_copy.remove(self.model._meta.pk.name)
            initial.update(model_to_dict(object_to_copy,
                                         fields=fields_to_copy))
        return initial

    def get_initial_inlines(self):
        initial_inlines = {}
        if self.request.GET.get('pk_copy', None) is not None:
            object_to_copy = get_object_or_404(self.get_queryset(), pk=self.request.GET['pk_copy'])
            for inline, inline_copy_fields in self.get_inlines_copy_fields().items():
                fields_to_copy = inline_copy_fields
                if inline.model._meta.pk.name in fields_to_copy:
                    fields_to_copy.remove(self.model._meta.pk.name)
                datas = []
                fk = _get_foreign_key(self.model, inline.model)
                for object in inline.model._default_manager.filter(**{fk.name: object_to_copy}):
                    datas.append(model_to_dict(object,
                                               fields=fields_to_copy))
                initial_inlines.update({inline: datas})
        return initial_inlines

    def dispatch(self, *args, **kwargs):
        self.object = None

        # BYPASS POST for initial data
        if self.request.META.get('HTTP_SEND_INITIAL_DATA') or \
            self.request.POST.get('SEND_INITIAL_DATA') or \
            self.request.GET.get('SEND_INITIAL_DATA'):
            if self.request.method == 'POST':
                self.send_initial_data = self.request.POST.dict()
                # switch to GET request
                self.request.method = 'GET'
                self.request.POST = QueryDict('', mutable=True)
            elif self.request.method == 'GET':
                self.send_initial_data = self.request.GET.dict()

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
        '''
        Before all data saving
        '''
        django_webix_view_pre_save.send(sender=self,
                                        instance=None,
                                        created=True,
                                        form=form,
                                        inlines=inlines)

    def post_form_save(self, form=None, inlines=None, **kwargs):
        '''
        After form save and before inlines save
        '''
        django_webix_view_pre_inline_save.send(sender=self,
                                               instance=self.object,
                                               created=True,
                                               form=form,
                                               inlines=inlines)

    def post_forms_valid(self, form=None, inlines=None, **kwargs):
        '''
        After all data saved
        '''
        django_webix_view_post_save.send(sender=self,
                                         instance=self.object,
                                         created=True,
                                         form=form,
                                         inlines=inlines)
        # LOG
        anonymous = self.request.user.is_anonymous() if callable(
            self.request.user.is_anonymous) else self.request.user.is_anonymous
        if self.logs_enable is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, ADDITION
            from django.contrib.contenttypes.models import ContentType
            LogEntry.objects.log_action(
                user_id=self.request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=ADDITION
            )

    def validate_unique_together(self, form=None, inlines=None, **kwargs):
        # self.object.validate_unique()
        if form is not None:
            form.instance.validate_unique()


class WebixUpdateView(WebixCreateUpdateMixin, WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin,
                      UpdateWithInlinesView):
    template_name = 'django_webix/generic/update.js'

    def get_form_kwargs(self):
        kwargs = super(WebixUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

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
        '''
        Before all data saving
        '''
        django_webix_view_pre_save.send(sender=self,
                                        instance=self.object,
                                        created=False,
                                        form=form,
                                        inlines=inlines)

    def post_form_save(self, form=None, inlines=None, **kwargs):
        '''
        After form save and before inlines save
        '''

        django_webix_view_pre_inline_save.send(sender=self,
                                               instance=self.object,
                                               created=False,
                                               form=form,
                                               inlines=inlines)

    def post_forms_valid(self, form=None, inlines=None, **kwargs):

        django_webix_view_post_save.send(sender=self,
                                         instance=self.object,
                                         created=False,
                                         form=form,
                                         inlines=inlines)

        anonymous = self.request.user.is_anonymous() if callable(
            self.request.user.is_anonymous) else self.request.user.is_anonymous
        if self.logs_enable is True and not anonymous and apps.is_installed('django.contrib.admin'):
            from django.contrib.admin.models import LogEntry, CHANGE
            from django.contrib.contenttypes.models import ContentType
            LogEntry.objects.log_action(
                user_id=self.request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_text(self.object),
                action_flag=CHANGE,
                change_message=_('Changed %s.') % get_text_list(form.changed_data, _('and'))
            )
