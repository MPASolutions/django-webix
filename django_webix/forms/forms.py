# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import copy
from collections import OrderedDict, defaultdict
from json import dumps, loads

import django
import six
from django import forms
from django.conf import settings

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, connection
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass, InlineForeignKeyField
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from random import randint
from sorl.thumbnail import get_thumbnail

try:
    from django.contrib.postgres.forms.jsonb import JSONField
except ImportError:
    JSONField = forms.Field

try:
    from django.contrib.postgres.fields.array import SimpleArrayField
except ImportError:
    SimpleArrayField = None

try:
    from django.contrib.gis.forms import GeometryField
except ImportError:
    GeometryField = None


class BaseWebixMixin(object):
    form_fix_height = None
    min_count_suggest = 100
    style = 'stacked'
    readonly_fields = []
    autocomplete_fields = []
    autocomplete_fields_urls = {}

    class Meta:
        localized_fields = '__all__'  # to use comma as separator in i18n

    def get_fields_data_with_prefix(self, data=None):
        readonly_fields = self.get_readonly_fields()
        if data is not None:
            qdict = data.copy()
            for name, field in copy.deepcopy(self.base_fields).items():
                key = self.add_prefix(name)
                if key in data and \
                    name not in readonly_fields:
                    if isinstance(field, forms.models.ModelMultipleChoiceField):
                        temp_list = []
                        if type(data[key]) != list:
                            for val in data[key].split(','):
                                if val != '':
                                    temp_list.append(val)
                        else:
                            temp_list = data[key]
                        qdict.setlist(key, temp_list)
                    else:
                        val = data[key]
                        qdict.update({key: val if val not in ['null', u'null'] else None})
            data = qdict
        return data

    def set_readonly_fields(self):
        # Replace field if it is in readonly_fields list
        for readonly_field in self.get_readonly_fields():
            try:
                _field = self._meta.model._meta.get_field(readonly_field)
            except FieldDoesNotExist:
                _field = None
            else:
                del self.fields[readonly_field]
                if not hasattr(self, 'instance') or self.instance.pk is None:
                    self.fields[readonly_field] = forms.CharField(
                        label=_(_field.verbose_name).capitalize(), required=False
                    )
                else:
                    if isinstance(_field, django.db.models.fields.DateTimeField) or \
                        isinstance(_field, django.forms.fields.DateTimeField) or \
                        isinstance(_field, django.forms.fields.DateTimeInput):
                        # TODO: it can be improved
                        self.fields[readonly_field] = forms.CharField(
                            label=_(_field.verbose_name).capitalize(),
                            required=False
                        )
                        if getattr(self.instance, readonly_field):
                            value = '{}'.format(getattr(self.instance, readonly_field).strftime('%d/%m/%Y %H:%i'))
                        else:
                            value = ''
                    elif isinstance(_field, django.db.models.fields.DateField) or \
                        isinstance(_field, django.forms.fields.DateField):
                        # TODO: it can be improved
                        self.fields[readonly_field] = forms.CharField(
                            label=_(_field.verbose_name).capitalize(),
                            required=False
                        )
                        if getattr(self.instance, readonly_field):
                            value = '{}'.format(getattr(self.instance, readonly_field).strftime('%d/%m/%Y'))
                        else:
                            value = ''
                    elif isinstance(_field, django.db.models.fields.BooleanField) or \
                        isinstance(_field, django.forms.fields.CheckboxInput):
                        # TODO: it can be improved
                        self.fields[readonly_field] = forms.BooleanField(
                            label=_(_field.verbose_name).capitalize(),
                            required=False
                        )
                        value = getattr(self.instance, readonly_field) or None
                    else:
                        self.fields[readonly_field] = forms.CharField(
                            label=_(_field.verbose_name).capitalize(),
                            required=False
                        )
                        value = '{}'.format(getattr(self.instance, readonly_field) or '')
                    self.fields[readonly_field].initial = value
                    self.initial[readonly_field] = value

    def webix_extra_clean(self, cleaned_data):
        for key, value in cleaned_data.items():
            if isinstance(value, six.string_types):
                cleaned_data[key] = value.strip()
        for _readonly_field in self.get_readonly_fields():
            cleaned_data.pop(_readonly_field, None)
        return cleaned_data

    def get_readonly_fields(self):
        """ Returns a list of readonly fields """
        if self.has_change_permission == False:
            readonly_fields = []
            for field_name in self.base_fields.keys():
                if not field_name.endswith('_block'):
                    readonly_fields.append(field_name)
            return readonly_fields
        else:
            return self.readonly_fields

    def _add_null_choice(self, choices):
        return [option for option in choices if option['id'] not in ['', u'', None]]

    def _get_url_suggest(self, app_label, model_name, to_field_name=None):
        """ Returns the url to autocomplete model choiche field """

        url = "{url}?app_label={app_label}&model_name={model_name}"
        if to_field_name:
            url += "&to_field={to_field}"
        return url.format(
            url=reverse('webix_autocomplete_lookup'),
            model_name=model_name,
            app_label=app_label,
            to_field=to_field_name,
        )

    @property
    def webix_id(self):
        """ Returns the form id """

        if hasattr(self.Meta, 'model'):
            return '{app_label}.{model_name}'.format(
                app_label=self.Meta.model._meta.app_label,
                model_name=self.Meta.model._meta.model_name
            )
        return self.__class__.__name__

    def get_rules(self):
        """ Returns the form rules """

        rules = defaultdict(list)
        for name, field in self.fields.items():
            if field.required and (not type(field) == forms.FileField or field.initial is not None):
                rules[self.add_prefix(name)].append({'rule': 'isNotEmpty'})
            if isinstance(field, forms.EmailField):
                rules[self.add_prefix(name)].append({'rule': 'isEmail'})
            elif isinstance(field, forms.FloatField):
                rules[self.add_prefix(name)].append({'rule': 'isNumber', 'min': -six.MAXSIZE, 'max': six.MAXSIZE})
            elif isinstance(field, forms.DecimalField):
                rules[self.add_prefix(name)].append({'rule': 'isNumber', 'min': -six.MAXSIZE, 'max': six.MAXSIZE})
            elif isinstance(field, forms.IntegerField):
                rules[self.add_prefix(name)].append({'rule': 'isInteger', 'min': -six.MAXSIZE, 'max': six.MAXSIZE})
            elif isinstance(field, forms.CharField):
                rules[self.add_prefix(name)].append({'rule': 'isString', 'min': 0, 'max': field.max_length})
        return dict(rules)

    @property
    def get_elements(self):
        """ Return an OrderedDict with all form fields in Webix format """

        elements = OrderedDict()
        for name, field in self.fields.items():
            _pass = False
            label = force_text(field.label).capitalize()
            if field.required:
                label = '<strong>{}</strong>'.format(label)
            el = {
                'view': 'text',
                'label': label,
                'name': self.add_prefix(name),
                'id': self[name].auto_id,
                'labelWidth': 200,
                'django_type_field': str(type(field).__name__),
            }

            if name in self.get_readonly_fields():
                el.update({
                    'disabled': True,
                    # 'id': '{}.{}'.format(self.webix_id, self[name].auto_id) # probabily old: disabled for has_change_permission=False
                })

            # Get initial value
            if hasattr(self, 'cleaned_data'):
                if type(field) == forms.models.ModelMultipleChoiceField:
                    initial = self.data.getlist(self.add_prefix(name), field.initial)
                elif connection.vendor == 'postgresql' and isinstance(field, JSONField):
                    initial = self.data.get(self.add_prefix(name), None)
                    if initial is not None:
                        initial = loads(initial)
                    else:
                        initial = field.initial
                else:
                    initial = self.data.get(self.add_prefix(name), field.initial)
            else:
                initial = self.initial.get(name, field.initial)

            # EmailField
            if isinstance(field, forms.EmailField):
                el.update({
                    'view': 'text'
                })
                if initial is not None:
                    el.update({'value': initial})
            # FloatField
            elif isinstance(field, forms.FloatField):
                if initial is not None:
                    el.update({'value': '{}'.format(initial).replace('.', ',')})
            # DecimalField
            elif isinstance(field, forms.DecimalField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({'value': '{}'.format(initial).replace('.', ',')})
            # IntegerField
            elif isinstance(field, forms.IntegerField):
                el.update({
                    'view': 'text'
                })
                if initial is not None and initial not in ['', None]:
                    el.update({'value': '{}'.format(initial)})
            # TimeField
            elif isinstance(field, forms.TimeField):
                el.update({
                    'view': "datepicker",
                    'type': "time",
                    'stringResult': True,
                    'editable': True
                })
                if initial is not None:
                    if isinstance(initial, six.string_types):
                        el.update({
                            'value': '{}'.format(initial).replace('-', ',').replace(' ', ',').replace(':', ',')
                        })
                    elif callable(initial):
                        el.update({'value': '{}'.format(initial().strftime('%H,%M'))})
                    else:
                        el.update({'value': '{}'.format(initial.strftime('%H,%M'))})
            # DateField
            elif isinstance(field, forms.DateField):
                el.update({
                    'view': 'datepicker',
                    'format': "%d/%m/%Y",
                    'stringResult': True,
                    'editable': True
                })
                if initial is not None:
                    if isinstance(initial, six.string_types):
                        el.update({'value': '{}'.format(initial[0:10]).replace('-', ',')})
                    elif callable(initial):
                        el.update({'value': '{}'.format(initial().strftime('%Y,%m,%d'))})
                    else:
                        el.update({'value': '{}'.format(initial.strftime('%Y,%m,%d'))})
            # DateTimeField
            elif isinstance(field, forms.DateTimeField):
                el.update({
                    'view': "datepicker",
                    'format': "%d/%m/%Y %H:%i",
                    'stringResult': True,
                    'timepicker': True,
                    'editable': True
                })
                if initial is not None:
                    if isinstance(initial, six.string_types):
                        el.update({
                            'value': '{}'.format(initial).replace('-', ',').replace(' ', ',').replace(':', ',')
                        })
                    elif callable(initial):
                        el.update({'value': '{}'.format(initial().strftime('%Y,%m,%d,%H,%M'))})
                    else:
                        el.update({'value': '{}'.format(initial.strftime('%Y,%m,%d,%H,%M'))})
            # BooleanField NullBooleanField
            elif isinstance(field, forms.NullBooleanField) or isinstance(field, forms.BooleanField):
                el.update({
                    'view': 'checkbox',
                    'checkValue': '2',
                    'uncheckValue': ''
                })
                if initial is not None:
                    if (isinstance(initial, bool) and initial) or \
                        (isinstance(initial, six.string_types) and initial.lower() == 'true') or \
                        (isinstance(initial, int) and initial == 2):
                        el.update({'value': '2'})
            # URLField
            elif isinstance(field, forms.URLField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({'value': initial})
            # SlugField
            elif isinstance(field, forms.SlugField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({'value': initial})
            # Image  # TODO
            elif 'image' in str(type(field)).lower():
                if initial is not None:
                    el.update({'value': None})
                el.update({
                    'view': 'uploader',
                    'autosend': False,
                    'multiple': False,
                    'width': 100,
                    'label': _('Upload new image')
                })
                if initial:
                    img_small = get_thumbnail(initial, '150x100', quality=85)
                    img_big = get_thumbnail(initial, '500x400', quality=85)
                    key = randint(1, 100000)
                    _template_file = '<img src="{}"  onclick="image_modal(\'{}\',{},{},\'{}\')">'.format(
                        img_small.url, img_big.url, 500, 400, str(key)
                    )
                else:
                    _template_file = ''
                elements.update({
                    '{}_block'.format(self[name].html_name): {
                        'cols': [
                            {
                                'name_label': name,
                                'id_label': 'label_' + name,
                                'borderless': True,
                                'template': label,
                                'height': 30,
                                'width': 200
                            },
                            {
                                'name_label': name,
                                'id_label': 'preview_' + name,
                                'borderless': True,
                                'template': _template_file,
                                'height': 100,
                                'width': 170
                            },
                            el,
                            {
                                'borderless': True,
                                'template': '',
                                'height': 30
                            },
                        ]}})
                _pass = True
            # FileField
            elif isinstance(field, forms.FileField):
                if initial is not None:
                    el.update({'value': None})
                el.update({
                    'view': 'uploader',
                    'autosend': False,
                    'multiple': False,
                    'directory': False,
                    'width': 100,
                    'label': _('Upload file')
                })
                if isinstance(field.widget, forms.widgets.FileInput):
                    directory = field.widget.attrs.get('directory', False)
                    multiple = field.widget.attrs.get('multiple', False),

                    el.update({
                        'multiple': field.widget.attrs.get('multiple', False),
                        'directory': field.widget.attrs.get('directory', False)
                    })

                    if directory:
                        el.update({
                            'label': _('Upload folder')
                        })

                    if multiple and not directory:
                        el.update({
                            'label': _('Upload files')
                        })

                _download = {}
                if initial:
                    _download = {
                        'name_label': name,
                        'id_label': name,
                        'borderless': True,
                        'view': "tootipButton",
                        "type": "iconButton",
                        "css": "webix_primary",
                        "icon": "fas fa-download",
                        "width": 35,
                        "on": {
                            "onItemClick": "(function (id, e) {{ window.open('{url}','_blank') }})".format(
                                url=initial.url if not isinstance(initial, six.string_types) else str(initial)
                            )
                        }
                    }
                elements.update({
                    '{}_block'.format(self[name].html_name): {
                        'cols': [
                            {
                                'name_label': name,
                                'id_label': name,
                                'borderless': True,
                                'template': label,
                                'height': 30
                            },
                            _download,
                            el
                        ]}})
                _pass = True
            # FilePathFied
            elif isinstance(field, forms.FilePathField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({'value': initial})
            # ModelMultipleChoiceField
            elif type(field) == forms.models.ModelMultipleChoiceField:
                if settings.WEBIX_LICENSE != 'PRO':
                    raise ImproperlyConfigured(
                        "MultipleChoiceField is available only with PRO webix license")
                if initial is not None:
                    el.update({
                        'value': ','.join([str(i.pk) if isinstance(i, models.Model) else str(i) for i in initial])
                    })
                count = field.queryset.count()

                if count > self.min_count_suggest and \
                    name not in self.autocomplete_fields:
                    self.autocomplete_fields.append(name)

                # autocomplete url
                if name in self.autocomplete_fields and \
                    name not in self.autocomplete_fields_urls:
                    self.autocomplete_fields_urls.update({
                        name: self._get_url_suggest(
                            field.queryset.model._meta.app_label,
                            field.queryset.model._meta.model_name,
                            field.to_field_name
                        )
                    })

                # autocomplete field
                if name in self.autocomplete_fields:
                    el.update({
                        "view": "multicombo",
                        'selectAll': True,
                        'placeholder': _('Click to select'),
                        'options': {
                            'dynamic': True,
                            'body': {
                                'data': [],
                                'dataFeed': self.autocomplete_fields_urls[name]
                            }
                        },
                    })
                    _vals = []
                    if 'value' in el:
                        _vals = el['value'].split(",")
                    for _val in [i for i in _vals if i != ''.strip()]:
                        if field.to_field_name:
                            record = field.queryset.get(**{field.to_field_name: _val})
                            el['options']['body']['data'].append({
                                'id': '{}'.format(getattr(record, field.to_field_name)),
                                'value': '{}'.format(record)
                            })
                        else:
                            record = field.queryset.get(pk=_val)
                            el['options']['body']['data'].append({
                                'id': '{}'.format(record.pk),
                                'value': '{}'.format(record)
                            })

                # regular field without autocomplete
                else:
                    el.update({
                        "view": "multicombo",
                        'selectAll': True,
                        'placeholder': _('Click to select'),
                        'options': {
                            'dynamic': True,
                            'body': {
                                'data': self._add_null_choice([{
                                    'id': '{}'.format(i.pk),
                                    'value': '{}'.format(i)
                                } for i in field.queryset])
                            }
                        },
                    })
                    # Default if is required and there are only one option
                    if field.required and initial is None and len(field.queryset) == 1:
                        el.update({'value': '{}'.format(field.queryset.first().pk)})
            # ModelChoiceField
            elif isinstance(field, forms.models.ModelChoiceField):
                if initial is not None:
                    el.update({'value': initial.pk if isinstance(initial, models.Model) else str(initial)})
                count = field.queryset.count()

                if count > self.min_count_suggest and \
                    name not in self.autocomplete_fields:
                    self.autocomplete_fields.append(name)

                # autocomplete url
                if name in self.autocomplete_fields and \
                    name not in self.autocomplete_fields_urls:
                    self.autocomplete_fields_urls.update({
                        name: self._get_url_suggest(
                            field.queryset.model._meta.app_label,
                            field.queryset.model._meta.model_name,
                            field.to_field_name
                        )
                    })

                # autocomplete field
                # if self.add_prefix(name)=='agrofarmacotrattamento_set-0-revisione_agrofarmaco':
                #    raise Exception(name, self.autocomplete_fields, self.autocomplete_fields_urls)

                if name in self.autocomplete_fields:
                    el.update({
                        'view': 'combo',
                        'placeholder': _('Click to select'),
                        'suggest': {
                            'view': "suggest",
                            'keyPressTimeout': 400,
                            'body': {
                                'data': [],
                                'dataFeed': self.autocomplete_fields_urls[name]
                            },
                        }
                    })
                    if 'value' in el and el['value'] != '':  # and int(el['value']) > 0:
                        if field.to_field_name:
                            record = field.queryset.get(**{field.to_field_name: el['value']})
                            el['suggest']['body']['data'] = [{
                                'id': '{}'.format(getattr(record, field.to_field_name)),
                                'value': '{}'.format(record)
                            }]
                        else:
                            record = field.queryset.get(pk=el['value'])
                            el['suggest']['body']['data'] = [{
                                'id': '{}'.format(record.pk),
                                'value': '{}'.format(record)
                            }]

                # regular field without autocomplete
                elif count <= 6:
                    choices = self._add_null_choice([{
                        'id': '{}'.format(i.pk),
                        'value': '{}'.format(i)
                    } for i in field.queryset])
                    if not field.required:
                        choices.insert(0, {'id': "", 'value': "------", '$empty': True})
                    el.update({
                        'options': choices,
                        'view': 'richselect',
                        'selectAll': True,
                        'placeholder': _('Click to select')
                    })
                    # Default if is required and there are only one option
                    if field.required and initial is None and len(field.queryset) == 1:
                        el.update({'value': '{}'.format(field.queryset.first().pk)})
                else:
                    el.update({
                        'view': 'combo',
                        'placeholder': _('Click to select'),
                        'options': self._add_null_choice([{
                            'id': '{}'.format(i.pk),
                            'value': '{}'.format(i)
                        } for i in field.queryset])
                    })
            # TypedChoiceField ChoiceField
            elif isinstance(field, forms.TypedChoiceField) or isinstance(field, forms.ChoiceField):
                choices = self._add_null_choice([{
                    'id': '{}'.format(key),
                    'value': '{}'.format(value)
                } for key, value in field._choices])
                if not field.required:
                    choices.insert(0, {'id': "", 'value': "------", '$empty': True})
                el.update({
                    'selectAll': True,
                    'view': 'richselect',
                    'placeholder': _('Click to select'),
                    'options': choices
                })
                if initial is not None:
                    el.update({'value': initial})
                # Default if is required and there are only one option
                if field.required and initial is None and len(field.choices) == 1:
                    el.update({'value': '{}'.format(field.choices[0][0])})

            # JSONField (postgresql)
            elif connection.vendor == 'postgresql' and isinstance(field, JSONField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    el.update({
                        'view': 'textarea'
                    })
                if initial is not None:
                    el.update({'value': dumps(initial)})

            # SimpleArrayField (postgresql)
            elif connection.vendor == 'postgresql' and \
                SimpleArrayField is not None and \
                isinstance(field, SimpleArrayField):
                if hasattr(field, 'base_field') and \
                    isinstance(field.base_field, forms.fields.DateField):
                    el.update({
                        'view': 'datepicker',
                        'multiselect': 'touch',
                        'format': "%d/%m/%Y",
                        'stringResult': True,
                    })
                if initial is not None:
                    if type(initial) == list:
                        el.update({
                            'value': ', '.join([i.strftime('%Y-%m-%d') for i in initial]),
                            'orig_value': ', '.join([i.strftime('%Y-%m-%d') for i in initial]),
                        })

            # CharField
            elif isinstance(field, forms.CharField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    el.update({
                        'view': 'textarea'
                    })
                if initial is not None:
                    el.update({'value': initial})

            # GeoFields
            elif GeometryField is not None and isinstance(field, GeometryField):
                el.update({
                    'view': 'textarea'
                })
                if initial is not None:
                    if issubclass(GEOSGeometry, django.contrib.gis.geos.GEOSGeometry) and \
                        isinstance(initial, GEOSGeometry):
                        el.update({'value': initial.ewkt})
                    elif type(initial) == str:
                        el.update({'value': str(initial)})
                    else:
                        raise Exception('Initial value {} for geo field {} is not supported'.format(initial, field))
            elif not isinstance(field, InlineForeignKeyField):
                raise Exception('Type of field {} not supported'.format(field))

            # widget RadioSelect
            if isinstance(field.widget, forms.RadioSelect):
                _choices = field.choices if hasattr(field, 'choices') else field.widget.choices
                el.update({
                    "view": "radio",
                    "options": [{
                        "id": key,
                        "value": value
                    } for key, value in _choices]
                })
                if initial is not None:
                    el.update({'value': initial})
                # Default if is required and there are only one option
                if field.required and initial is None and len(_choices) == 1:
                    el.update({'value': '{}'.format(_choices[0][0])})

            # widget Hidden Fields
            if type(field.widget) == forms.widgets.HiddenInput:
                el.update({'hidden': True})

            # Delete checkbox hidden
            if self.add_prefix(name).endswith('-DELETE'):
                el.update({'hidden': True})
                elements.update({
                    "{}-icon".format(self.add_prefix(name)): {
                        'view': "button",
                        'type': "icon",
                        'icon': "far fa-trash-alt",
                        'align': "center",
                        'width': 28,
                        'hidden': not (self.has_delete_permission is not None and self.has_delete_permission == True),
                        'id': "{}-icon".format(self.add_prefix(name))
                    }
                })

            if not _pass:
                elements.update({self.add_prefix(name): el})

        return elements

    @property
    def get_tabular_fields_header(self):
        """ Returns the header for the tabular inlines as webix js format """

        fields_header = OrderedDict()
        # for name, f in self.fields.items():
        for field_name, f in self.get_elements.items():

            _field_header = None

            if 'hidden' not in f or 'hidden' in f and not f['hidden']:

                _field_header = {}

                if field_name.endswith('-DELETE'):
                    _field_header = {'header': '', 'width': 28}
                else:
                    if 'width' in f:
                        _field_header.update({'width': f['width']})
                    else:
                        _field_header.update({'fillspace': True})

                if 'header' in f:
                    if not isinstance(f['header'], list):
                        f['header'] = [f['header']]
                    _field_header.update({'header': f['header']})
                elif 'label' in f:
                    _field_header.update({'header': force_text(f['label']).capitalize()})

                if _field_header is not None:
                    fields_header.update({field_name: _field_header})

        return fields_header

    @property
    def get_tabular_header(self):
        """ Returns the header for the tabular inlines as webix js format """
        return dumps({
            'id': self.add_prefix('datatable'),
            'view': "datatable",
            'scroll': 'false',
            'autoheight': 'false',
            'data': [],
            'columns': list(self.get_tabular_fields_header.values()),
        }, cls=DjangoJSONEncoder)

    def as_webix(self):
        """ Webix js format form structure """

        return dumps(list(self.get_fieldsets()), cls=DjangoJSONEncoder)[1:-1]

    def get_fieldsets(self, **kwargs):
        """ Returns a dict with all the fields """

        if 'fs' in kwargs:
            fs = kwargs['fs']
        else:
            fs = self.get_elements
        if self.style == 'tabular':
            for field in fs:
                fs[field]['label'] = ''
                fs[field]['labelWidth'] = 0
        return fs.values()


####################### BaseWebixForm AND BaseWebixModelForm #######################

class BaseWebixForm(forms.BaseForm, BaseWebixMixin):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None, request=None, inline_id=None,
                 has_add_permission=None, has_change_permission=None, has_delete_permission=None):
        # Set request
        self.request = request
        self.has_add_permission = has_add_permission
        self.has_change_permission = has_change_permission
        self.has_delete_permission = has_delete_permission

        # Set inline id
        self.inline_id = inline_id

        # Set form prefix
        if prefix is not None:
            self.prefix = prefix

        # Update field names with prefix
        data = self.get_fields_data_with_prefix(data)

        super(BaseWebixForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                            empty_permitted, field_order, use_required_attribute, renderer)

        # TODO: check if it works with all field types on create and update action
        self.set_readonly_fields()

    def clean(self):
        cleaned_data = super(BaseWebixForm, self).clean()
        cleaned_data = self.webix_extra_clean(cleaned_data)
        return cleaned_data


class BaseWebixModelForm(forms.BaseModelForm, BaseWebixMixin):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None, request=None, inline_id=None,
                 has_add_permission=None, has_change_permission=None, has_delete_permission=None):
        # Set request
        self.request = request
        self.has_add_permission = has_add_permission
        self.has_change_permission = has_change_permission
        self.has_delete_permission = has_delete_permission

        # Set inline id
        self.inline_id = inline_id

        # Set form prefix
        if prefix is not None:
            self.prefix = prefix

        # Update field names with prefix
        data = self.get_fields_data_with_prefix(data)

        if django.VERSION > (2, 0):
            super(BaseWebixModelForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                     empty_permitted, instance, use_required_attribute, renderer)
        else:
            super(BaseWebixModelForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix,
                                                     empty_permitted, instance, use_required_attribute)

        # TODO: check if it works with all field types on create and update action
        self.set_readonly_fields()

    def clean(self):
        cleaned_data = super(BaseWebixModelForm, self).clean()
        cleaned_data = self.webix_extra_clean(cleaned_data)
        return cleaned_data

    def get_name(self):
        return capfirst(self.Meta.model._meta.verbose_name)


####################### WebixForm AND WebixModelForm #######################


class WebixForm(six.with_metaclass(DeclarativeFieldsMetaclass, BaseWebixForm)):
    pass


class WebixModelForm(six.with_metaclass(ModelFormMetaclass, BaseWebixModelForm)):
    pass
