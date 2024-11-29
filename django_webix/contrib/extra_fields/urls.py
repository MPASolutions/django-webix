from django.urls import path
from django_webix.contrib.extra_fields.views import ModelFieldConfigView

urlpatterns = [
    path(
        "extra_fields/model_field/<int:pk>/config",
        ModelFieldConfigView.as_view(),
        name="dwextra_fields.modelfield.config",
    )
]
