from django.urls import path

from django_webix.contrib.auth.views import (WebixPasswordResetContainerView,
                                             WebixPasswordResetView,
                                             WebixPasswordResetDoneView,
                                             WebixPasswordResetConfirmView,
                                             WebixPasswordResetCompleteView)

urlpatterns = [
    path('password_reset/', WebixPasswordResetContainerView.as_view(), name='dwauth.password_reset.base'),
    path('password_reset/form/', WebixPasswordResetView.as_view(), name='dwauth.password_reset.form'),
    path('password_reset/done/', WebixPasswordResetDoneView.as_view(), name='dwauth.password_reset.done'),
    path('reset/<uidb64>/<token>/', WebixPasswordResetConfirmView.as_view(), name='dwauth.password_reset.confirm'),
    path('reset/done/', WebixPasswordResetCompleteView.as_view(), name='dwauth.password_reset.complete'),
]
