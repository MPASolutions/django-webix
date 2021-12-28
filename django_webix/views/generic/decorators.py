# -*- coding: utf-8 -*-

import json

from django.http import JsonResponse
from django.utils.translation import gettext as _


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
):  # TODO: permission check before execution

    if allowed_permissions is None:
        allowed_permissions = []

    if response_type not in ['json', 'script', 'blank']:
        raise Exception('No valid response_type [json,script,blank]')

    def decorator(func):
        def wrapper(self, request, qs):
            if form is not None:
                if request.method == 'POST':
                    try:
                        params = json.loads(request.POST.get('params', '{}'))
                    except json.JSONDecodeError:
                        params = {}
                    _form = form(params, request.FILES, request=request)
                    if _form.is_valid():
                        return func(self, request, qs, _form)
                    else:
                        return JsonResponse({
                            'status': False,
                            'errors': [', '.join(['{}: {}'.format(k, v) for k, v in _form.errors.items()])]
                        }, status=400)
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

        return wrapper

    return decorator
