
from django.apps import apps
from django.contrib.gis.db import models

geo_field_classes = {
    "POINT": models.PointField,
    "MULTIPOINT": models.MultiPointField,
    "LINESTRING": models.LineStringField,
    "MULTILINESTRING": models.MultiLineStringField,
    "POLYGON": models.PolygonField,
    "MULTIPOLYGON": models.MultiPolygonField,
    "GEOMETRYCOLLECTION": models.GeometryCollectionField,
    "GEOMETRY": models.GeometryField
}


def get_model_geo_field_names(model):
    geo_field_names = []
    for field in model._meta.fields:
        if type(field) in geo_field_classes.values():
            geo_field_names.append(field.name)
    return geo_field_names


def get_layers(model, qxs_layers=None, geo_field_name=None):
    layers = []

    if apps.is_installed("qxs") and \
        apps.is_installed("django_webix_leaflet") and \
        model is not None:
        from qxs.registry import qxsreg  # FIXME: add to requirements?

        if qxs_layers is not None:
            for layer_name in qxs_layers:
                model_qxs = qxsreg.get_model(layer_name)
                if model_qxs.model == model:
                    layers.append({
                        'codename': model_qxs.get_qxs_codename(),
                        'layername': model_qxs.get_title(),
                        'qxsname': model_qxs.get_qxs_name(),
                        'geofieldname': model_qxs.geo_field_name
                    })
                else:
                    raise Exception('DjangoWebix: view configured with mismatching qxs model: {} [{} x {}]'.format(
                        layer_name, model, model_qxs.model)
                    )

        else:
            for model_qxs in list(filter(lambda mqxs: mqxs.model == model, qxsreg.get_models())):
                if geo_field_name is None or model_qxs.geo_field_name == geo_field_name:
                    layers.append({
                        'codename': model_qxs.get_qxs_codename(),
                        'layername': model_qxs.get_title(),
                        'qxsname': model_qxs.get_qxs_name(),
                        'geofieldname': model_qxs.geo_field_name
                    })

    return layers
