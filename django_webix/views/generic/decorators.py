import json

from django.apps import apps
from django.http import JsonResponse, QueryDict
from django.utils.translation import gettext_lazy as _
from django_webix.views import WebixTemplateView, WebixFormView


class DynamicTemplateFormView(WebixFormView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset'] = kwargs.get('queryset')
        context['parent_view'] = kwargs.get('parent_view')
        return context


def action_config(
    action_key,
    response_type,
    allowed_permissions=None,
    short_description=None,
    modal_header=_('Fill in the form'),
    modal_title=_("Are you sure you want to proceed with this action?"),
    modal_click=_("Go"),
    modal_ok=_("Proceed"),
    modal_cancel=_("Undo"),
    form=None,
    reload_list=True,
    maximum_count=None,
    template_view=None,
    dynamic=False,
    form_view=DynamicTemplateFormView,
    form_view_template=None,
):  # TODO: permission check before execution
    """
    Decorator to configure action on list

    :param action_key: action code name
    :param response_type: type of http response, options: 'json', 'script', 'blank'
    :param allowed_permissions: list of permission required to execute the action
    :param short_description: description to show on list toolbar
    :param modal_header: title of the modal header
    :param modal_title: description of the modal to display
    :param modal_click: text of form button confirm
    :param modal_ok: text of confirmation button
    :param modal_cancel: text to discard changes
    :param form: (optional) form to show before execute the action
    :param reload_list: indicates whether to reload the list after executing the action
    :param maximum_count: (optional) maximim number of selected elements
    :param template_view: (optional) TemplateView to render before the action
    :param dynamic: (optional) boolean for obtain a dynamic action load
    :param form_view: (optional) FormView for dynamic render action window
    :param form_view_template: (optional) FormView template for dynamic render action window
    :return:
        - response_type: json
        JsonResponse with 'status', 'message', 'message_on_popup', 'message_type' keys
            status: (bool) indicates if status is successfull
            message: text to display
            message_on_popup: (bool) show message as webix alert or message
            message_type: type of webix alert or message

        e.g.: JsonResponse({'status': True, 'message': 'my message', 'message_on_popup': True, 'message_type': 'info'})

        - response_type: script
        HttpResponse with javascript content

        e.g.: HttpResponseRedirect(reverse('my-url'))

        - response_type: blank
        HttpResponse with any type of content

        e.g.: HttpResponse(content_type='application/octet-stream')
    """

    if allowed_permissions is None:
        allowed_permissions = []

    if response_type not in ['json', 'script', 'blank']:
        raise Exception('No valid response_type [json,script,blank]')

    if template_view is not None and not issubclass(template_view, WebixTemplateView):
        raise Exception("No valid template_view class, it must be subclass of WebixTemplateView")

    if form_view is not None and not issubclass(form_view, WebixFormView):
        raise Exception("No valid form_view class, it must be subclass of WebixFormView")

    def decorator(func):
        def wrapper(self, request, qs):

            if maximum_count is not None and qs.only(qs.model._meta.pk.name).count() > maximum_count:
                return JsonResponse({
                    'status': False,
                    'errors': [_('You can perform this action on a maximum of {} raws').format(maximum_count)]
                }, status=400)

            if template_view is not None and request.method == 'POST' and request.POST.get('template_view'):
                request.method = 'GET'  # convert request from POST to GET

                def get_context_data_webix_base(self, request, **kwargs):
                    context = super(template_view, self).get_context_data_webix_base(request, **kwargs)
                    context['action_key'] = action_key
                    context['webix_container_id'] = f'{action_key}_win_body'
                    return context

                template_view.get_context_data_webix_base = get_context_data_webix_base

                return template_view.as_view()(request, queryset=qs, action_key=action_key)

            elif dynamic is not None and request.method == 'POST' and request.POST.get('dynamic'):
                request.method = 'GET'  # convert request from POST to GET

                def get_context_data_webix_base(self, request, **kwargs):
                    context = super(form_view, self).get_context_data_webix_base(request, **kwargs)
                    context.update({
                        'ids': request.POST.get('ids'),
                        'all': request.POST.get('all'),
                        'action_key': action_key,
                        'response_type': response_type,
                        'short_description': short_description,
                        'modal_header': modal_header,
                        'modal_title': modal_title,
                        'modal_click': modal_click,
                        'modal_ok': modal_ok,
                        'modal_cancel': modal_cancel,
                        'reload_list': reload_list
                        # 'form': form # form is passed by view by default with all data filled-in
                    })
                    context['webix_container_id'] = f'{action_key}_win'

                    return context

                form_view.get_context_data_webix_base = get_context_data_webix_base

                form_view.template_name = 'django_webix/include/action_dynamic.js' if form_view_template is None else form_view_template

                form_view.form_class = form

                return form_view.as_view()(request, queryset=qs, parent_view=self, action_key=action_key)

            elif form is not None and request.method == 'POST':
                try:
                    params = QueryDict(mutable=True)
                    params.update(json.loads(request.POST.get('params', '{}')))
                except json.JSONDecodeError:
                    params = QueryDict()

                _form = form(params, request.FILES, request=request, **{'queryset': qs})
                if _form.is_valid():
                    anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else \
                        request.user.is_anonymous
                    if not anonymous and apps.is_installed('django.contrib.admin'):
                        from django.contrib.admin.models import LogEntry, CHANGE
                        from django.contrib.contenttypes.models import ContentType
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                            object_id=None,  # on a QS
                            object_repr=','.join([str(i) for i in qs.values_list('pk', flat=True)]),
                            action_flag=CHANGE,
                            change_message=_('Action success: {} data:{}').format(
                                wrapper.short_description,
                                _form.cleaned_data
                            )
                        )

                    return func(self, request, qs, _form)
                else:
                    return JsonResponse({
                        'status': False,
                        'errors': [{"label": None, "error": error} for error in _form.non_field_errors()] +
                                  [{"label": field.label, "error": error}
                                   for field in _form for error in field.errors]
                    }, status=400)
            else:
                anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else \
                    request.user.is_anonymous
                if not anonymous and apps.is_installed('django.contrib.admin'):
                    from django.contrib.admin.models import LogEntry, CHANGE
                    from django.contrib.contenttypes.models import ContentType
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                        object_id=None,  # on a QS
                        object_repr=','.join([str(i) for i in qs.values_list('pk', flat=True)]),
                        action_flag=CHANGE,
                        change_message=_('Action success: {}').format(wrapper.short_description)
                    )

            return func(self, request, qs)

        setattr(wrapper, 'action_key', action_key)
        setattr(wrapper, 'response_type', response_type)
        setattr(wrapper, 'allowed_permissions', allowed_permissions)
        setattr(wrapper, 'short_description', short_description)
        setattr(wrapper, 'modal_header', modal_header)
        setattr(wrapper, 'modal_title', modal_title)
        setattr(wrapper, 'modal_click', modal_click)
        setattr(wrapper, 'modal_ok', modal_ok)
        setattr(wrapper, 'modal_cancel', modal_cancel)
        setattr(wrapper, 'form', form)
        setattr(wrapper, 'reload_list', reload_list)
        setattr(wrapper, 'maximum_count', maximum_count)
        setattr(wrapper, 'template_view', template_view)
        setattr(wrapper, 'dynamic', dynamic)
        setattr(wrapper, 'form_view', form_view)
        setattr(wrapper, 'form_view_template', form_view_template)

        return wrapper

    return decorator
