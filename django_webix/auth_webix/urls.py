# -*- coding: utf-8 -*-

from django.urls import path

from django_webix.auth_webix.views import (
    WebixPasswordResetContainerView, WebixPasswordResetView, WebixPasswordResetDoneView, WebixPasswordResetConfirmView,
    WebixPasswordResetCompleteView
)

urlpatterns = [
    path('password_reset/', WebixPasswordResetContainerView.as_view(), name='base_password_reset'),
    path('password_reset/form/', WebixPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', WebixPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', WebixPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', WebixPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
