import json

from django.http import JsonResponse, QueryDict
from django.utils.translation import gettext_lazy as _


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
    ):  # TODO: permission check before execution

    if allowed_permissions is None:
        allowed_permissions = []

    if response_type not in ['json', 'script', 'blank']:
        raise Exception('No valid response_type [json,script,blank]')

    def decorator(func):
        def wrapper(self, request, qs):
            if maximum_count is not None and qs.count() > maximum_count:
                return JsonResponse({
                    'status': False,
                    'errors': [_('You can perform this action on a maximum of {} raws').format(maximum_count)]
                }, status=400)

            if form is not None:
                if request.method == 'POST':
                    try:
                        params = QueryDict(mutable=True)
                        params.update(json.loads(request.POST.get('params', '{}')))
                    except json.JSONDecodeError:
                        params = QueryDict()
                    _form = form(params, request.FILES, request=request)
                    if _form.is_valid():
                        # log execute action
                        from django.contrib.admin.models import LogEntry, CHANGE
                        from django.contrib.contenttypes.models import ContentType
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                            object_id=None, # on a QS
                            object_repr=','.join([str(i) for i in qs.values_list('id',flat=True)]),
                            action_flag=CHANGE,
                            change_message=_('Action success: {} data:{}').format(wrapper.short_description,
                                                                               _form.cleaned_data)
                            )
                        return func(self, request, qs, _form)
                    else:
                        return JsonResponse({
                            'status': False,
                            'errors': [', '.join(['{}: {}'.format(k, v) for k, v in _form.errors.items()])]
                        }, status=400)
            else:
                # log execute action
                from django.contrib.admin.models import LogEntry, CHANGE
                from django.contrib.contenttypes.models import ContentType
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                    object_id=None,  # on a QS
                    object_repr=','.join([str(i) for i in qs.values_list('id', flat=True)]),
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

        return wrapper

    return decorator
