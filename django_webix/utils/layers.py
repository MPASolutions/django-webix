# -*- coding: utf-8 -*-

from django.apps import apps


def get_layers(model, geo_field_name=None):
    layers = []

    if apps.is_installed("qxs") and \
        apps.is_installed("django_webix_leaflet") and \
        model is not None:
        from qxs import qxsreg  # FIXME: add to requirements?

        for model_layer in list(filter(lambda x: x.model == model, qxsreg.get_models())):
            if geo_field_name is None or model_layer.geo_field_name == geo_field_name:
                layers.append({
                    'codename': model_layer.get_qxs_codename(),
                    'layername': model_layer.get_title(),
                    'qxsname': model_layer.get_qxs_name(),
                    'geofieldname': model_layer.geo_field_name
                })

    return layers
