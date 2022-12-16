from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.validators import BaseValidator
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

class AutoMultiPolygonField(forms.MultiPolygonField):

    def __init__(self, *args, **kwargs):
        self.source_srid = kwargs.pop('source_srid', None)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        geo = GEOSGeometry(value)

        # only if there is geometry, because the 'geometry' field is always added by the validator
        if not geo.empty:

            # set geometry srid
            if geo.srid is None:
                if self.source_srid is not None:
                    geo.srid = self.source_srid
                else:
                    raise Exception('Error: missing geometry field SRID')

            # convert geometry to MultiPolygon
            if geo.geom_type == 'Polygon':
                return MultiPolygon(geo, srid=geo.srid)
            else:
                return geo

        else:
            return None


class ModelChoiceZFillField(forms.ModelChoiceField):
    def __init__(self, zfill=0, *args, **kwargs):
        self.zfill = zfill
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return
        return super().to_python(str(value).zfill(self.zfill))
