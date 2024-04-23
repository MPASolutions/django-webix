from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.validators import BaseValidator
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.utils.encoding import force_str


def validate_truefalse(value):
    true_vals = ['true', 't', 'si', 'sì', 's', 'yes', 'y', 'ja', 'j', 'oui', 'o', '1', 'x']
    false_vals = ['false', 'f', 'no', 'n', 'nein', 'kein', 'keine', 'k', 'non', 'aucun', 'a', '0']

    norm_val = str(value).lower()
    if norm_val in true_vals:
        return True
    elif norm_val in false_vals:
        return False
    else:
        raise forms.ValidationError(
            _('%(value)s is not a boolean value'),
            params={'value': value},
        )


class StrictMinValueValidator(BaseValidator):
    message = _('Ensure this value is strictly greater than %(limit_value)s.')
    code = 'min_value'

    def compare(self, a, b):
        return a <= b


class SlugifyCharField(forms.CharField):
    def to_python(self, value):
        return slugify(value)


class SlugifyChoiceField(forms.ChoiceField):
    def to_python(self, value):
        "Returns a Unicode object."
        if value in self.empty_values:
            return ''
        return slugify(force_str(value))


class AutoMultiGeometryField(forms.GeometryField):

    def __init__(self, *, source_srid=None, **kwargs):
        """

        :param source_srid: optional parameter defined in impotrer form field to define/overwrite the sorce data srid
        :param kwargs:

        Example:
        geo = AutoMultiPolygonField(required=True, label='WKT', srid=settings.SRS, source_srid=3003)
        """
        self.source_srid = source_srid
        super().__init__(**kwargs)

    def to_python(self, value):
        geom = super().to_python(value)

        if geom is not None:
            if self.source_srid is not None:
                geom.srid = self.source_srid

            if 'MULTI' + str(geom.geom_type).upper() == self.geom_type:
                geom = import_string('django.contrib.gis.geos.Multi' + geom.geom_type)(geom, srid=geom.srid)

        return geom


class AutoPointField(AutoMultiGeometryField):
    geom_type = "POINT"


class AutoMultiPointField(AutoMultiGeometryField):
    geom_type = "MULTIPOINT"


class AutoLineStringField(AutoMultiGeometryField):
    geom_type = "LINESTRING"


class AutoMultiLineStringField(AutoMultiGeometryField):
    geom_type = "MULTILINESTRING"


class AutoPolygonField(AutoMultiGeometryField):
    geom_type = "POLYGON"


class AutoMultiPolygonField(AutoMultiGeometryField):
    geom_type = "MULTIPOLYGON"


class ModelChoiceZFillField(forms.ModelChoiceField):
    def __init__(self, zfill=0, *args, **kwargs):
        self.zfill = zfill
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return
        return super().to_python(str(value).zfill(self.zfill))
