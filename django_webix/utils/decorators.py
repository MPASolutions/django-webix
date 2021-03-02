# -*- coding: utf-8 -*-

from functools import wraps

from django.conf import settings
from django.shortcuts import render


def script_login_required(view, login_url=None):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'django_webix/redirect_to_login.js', context={
                'login_url': login_url or settings.LOGIN_URL
            })
        return view(request, *args, **kwargs)

    return wrapper
