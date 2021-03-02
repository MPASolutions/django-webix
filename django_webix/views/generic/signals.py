# -*- coding: utf-8 -*-

from django.dispatch import Signal

django_webix_view_pre_delete = Signal(providing_args=['instance'])
django_webix_view_post_delete = Signal(providing_args=['instance'])

django_webix_view_pre_save = Signal(providing_args=['instance', 'created', 'form', 'inlines'])
django_webix_view_pre_inline_save = Signal(providing_args=['instance', 'created', 'form', 'inlines'])
django_webix_view_post_save = Signal(providing_args=['instance', 'created', 'form', 'inlines'])
