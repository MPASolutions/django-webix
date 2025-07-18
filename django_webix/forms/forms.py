import copy
import datetime
import os
from collections import OrderedDict, defaultdict
from json import dumps, loads
from random import randint

import django
import six
from django import forms
from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, models
from django.forms.fields import JSONField
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass
from django.forms.utils import ErrorList
from django.urls import reverse
from django.utils import formats
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode
from django.utils.text import capfirst
from django.utils.timezone import is_naive, make_naive
from django.utils.translation import gettext_lazy as _
from django_webix.utils.layers import get_layers
from sorl.thumbnail import get_thumbnail

try:
    from django.utils.encoding import force_text as force_str
except ImportError:
    from django.utils.encoding import force_str

try:
    from phonenumber_field.formfields import PhoneNumberField
except ImportError:
    PhoneNumberField = None

try:
    from django.contrib.postgres.forms import SimpleArrayField
except ImportError:
    SimpleArrayField = None

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.forms import (  # noqa: F401
        GeometryField,
        LineStringField,
        MultiLineStringField,
        MultiPolygonField,
        PointField,
        PolygonField,
    )
except ImportError:
    GeometryField = None
    PointField = None


class BaseWebixMixin:

    warnings = []

    form_fix_height = None
    min_count_suggest = 100
    style = "stacked"
    label_width = 300
    label_width_mobile = 120
    suggest_width = None  # options : int | None for width as parent
    label_align = "left"
    help_text_template = "&nbsp;<i style='font-size:14px;' class='webix_icon far fa-info-circle'></i>"

    class Meta:
        localized_fields = "__all__"  # to use comma as separator in i18n

    def get_label_width(self):
        if self.request is not None and hasattr(self.request, "user_agent") and self.request.user_agent.is_mobile:
            return self.label_width_mobile
        return self.label_width

    def get_suggest_width(self):
        return self.suggest_width

    def get_label_align(self):
        return self.label_align

    def get_fields_data_with_prefix(self, data=None):
        readonly_fields = self.get_readonly_fields()
        if data is not None:
            qdict = data.copy()
            for name, field in copy.deepcopy(self.base_fields).items():
                key = self.add_prefix(name)
                if key in data and name not in readonly_fields:
                    if isinstance(field, (forms.models.ModelMultipleChoiceField, forms.MultipleChoiceField)):
                        temp_list = []
                        # it must be "type" and not "isinstance" because QueryDict is inherited from MultiValueDict
                        if type(data) is MultiValueDict:
                            temp_list = data.getlist(key)
                        elif type(data[key]) is not list:
                            for val in data[key].split(","):
                                if val != "":
                                    temp_list.append(val)
                        else:
                            temp_list = data[key]
                        qdict.setlist(key, temp_list)
                    else:
                        val = data[key]
                        qdict.update({key: val if val not in ["null"] else None})
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

                if (
                    isinstance(_field, django.db.models.fields.DateTimeField)
                    or isinstance(_field, django.forms.fields.DateTimeField)
                    or isinstance(_field, django.forms.fields.DateTimeInput)
                ):
                    # TODO: it can be improved
                    self.fields[readonly_field] = forms.CharField(
                        label=capfirst(_field.verbose_name.strip()), required=False
                    )
                    if (
                        hasattr(self, "instance")
                        and self.instance.pk is not None
                        and getattr(self.instance, readonly_field)
                    ):
                        _value = getattr(self.instance, readonly_field)
                        if not is_naive(_value):
                            _value = make_naive(_value)
                        value = "{}".format(_value.strftime("%d/%m/%Y %H:%M"))
                    else:
                        value = ""
                elif isinstance(_field, django.db.models.fields.DateField) or isinstance(
                    _field, django.forms.fields.DateField
                ):
                    # TODO: it can be improved
                    self.fields[readonly_field] = forms.CharField(
                        label=capfirst(_field.verbose_name.strip()), required=False
                    )
                    if (
                        hasattr(self, "instance")
                        and self.instance.pk is not None
                        and getattr(self.instance, readonly_field)
                    ):
                        value = "{}".format(getattr(self.instance, readonly_field).strftime("%d/%m/%Y"))
                    else:
                        value = ""
                elif isinstance(_field, django.db.models.fields.BooleanField) or isinstance(
                    _field, django.forms.fields.CheckboxInput
                ):
                    # TODO: it can be improved
                    self.fields[readonly_field] = forms.BooleanField(
                        label=capfirst(_field.verbose_name.strip()), required=False
                    )
                    if hasattr(self, "instance") and self.instance.pk is not None:
                        value = getattr(self.instance, readonly_field) or None
                    else:
                        value = None
                else:
                    self.fields[readonly_field] = forms.CharField(
                        label=capfirst(_field.verbose_name.strip()), required=False
                    )
                    if hasattr(self, "instance") and self.instance.pk is not None:
                        value = (
                            "{}".format(getattr(self.instance, readonly_field))
                            if getattr(self.instance, readonly_field) is not None
                            else ""
                        )
                    else:
                        value = ""

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
        """Returns a list of readonly fields"""
        if self.has_change_permission is False:
            readonly_fields = []
            for field_name in self.base_fields.keys():
                if not field_name.endswith("_block"):
                    readonly_fields.append(field_name)
            return readonly_fields
        else:
            return self.readonly_fields

    def _add_null_choice(self, choices):
        return [option for option in choices if option["id"] not in ["", None]]

    def _get_url_suggest(self, app_label, model_name, to_field_name=None, limit_choices_to=None):
        """Returns the url to autocomplete model choiche field"""

        url = "{url}?app_label={app_label}&model_name={model_name}"
        if to_field_name:
            url += "&to_field={to_field}"
        if limit_choices_to is not None and limit_choices_to != {}:
            from django.contrib.admin.widgets import url_params_from_lookup_dict

            dict_limit_choices_to = url_params_from_lookup_dict(limit_choices_to)
            url += "&query_string=" + urlencode(dict_limit_choices_to).replace("&", ":")

        return url.format(
            url=reverse("webix_autocomplete_lookup"),
            model_name=model_name,
            app_label=app_label,
            to_field=to_field_name,
        )

    def get_model(self):
        if hasattr(self.Meta, "model"):
            return self.Meta.model
        else:
            return None

    @property
    def webix_id(self):
        """Returns the form id"""
        model = self.get_model()
        if model is not None:
            return "{app_label}.{model_name}".format(
                app_label=model._meta.app_label, model_name=model._meta.model_name
            )
        return self.__class__.__name__

    def get_rules(self):
        """Returns the form rules"""

        rules = defaultdict(list)
        for name, field in self.fields.items():
            if field.required and (not isinstance(field, forms.FileField) or field.initial is not None):
                rules[self.add_prefix(name)].append({"rule": "isNotEmpty"})
            if isinstance(field, forms.EmailField):
                rules[self.add_prefix(name)].append({"rule": "isEmail"})
            elif isinstance(field, forms.FloatField):
                rules[self.add_prefix(name)].append({"rule": "isNumber", "min": -six.MAXSIZE, "max": six.MAXSIZE})
            elif isinstance(field, forms.DecimalField):
                rules[self.add_prefix(name)].append({"rule": "isNumber", "min": -six.MAXSIZE, "max": six.MAXSIZE})
            elif isinstance(field, forms.IntegerField):
                rules[self.add_prefix(name)].append({"rule": "isInteger", "min": -six.MAXSIZE, "max": six.MAXSIZE})
            elif isinstance(field, forms.CharField) and (
                SimpleArrayField is not None and not isinstance(field, SimpleArrayField)
            ):
                rules[self.add_prefix(name)].append({"rule": "isString", "min": 0, "max": field.max_length})
        return dict(rules)

    @property
    def get_elements(self):
        """Return an OrderedDict with all form fields in Webix format"""

        elements = OrderedDict()
        for name, field in self.fields.items():
            _pass = False
            label = capfirst(force_str(field.label).strip())
            el = {
                "view": "text",
                "label": label,
                "name": self.add_prefix(name),
                "id": self[name].auto_id,
                "labelWidth": self.get_label_width(),
                "labelAlign": self.get_label_align(),
                "django_type_field": str(type(field).__name__),
            }

            if field.required:
                el["label"] = label = "<strong>{}</strong>".format(label)
                # el['required'] = True  # FIXME: problems with inlines

            if hasattr(field, "help_text") and field.help_text is not None and field.help_text != "":
                el["tooltip"] = {"template": "{}".format(field.help_text)}
                el["label"] = el["label"] + self.help_text_template

            if name in self.get_readonly_fields():
                el.update(
                    {
                        "disabled": True,
                    }
                )

            # Get initial value
            if hasattr(self, "cleaned_data"):
                if isinstance(field, (forms.models.ModelMultipleChoiceField, forms.MultipleChoiceField)):
                    initial = self.data.getlist(self.add_prefix(name), field.initial)
                elif connection.vendor == "postgresql" and isinstance(field, JSONField):
                    initial = self.data.get(self.add_prefix(name), None)
                    if initial is not None and initial != "":
                        try:
                            initial = loads(initial)
                        except Exception:  # if not valid do nothing
                            pass
                    else:
                        initial = field.initial
                else:
                    initial = self.data.get(self.add_prefix(name), field.initial)
            else:
                initial = self.initial.get(name, field.initial)

            # EmailField
            if isinstance(field, forms.EmailField):
                el.update({"view": "text"})
                if initial is not None:
                    el.update({"value": initial})
            # FloatField
            elif isinstance(field, forms.FloatField):
                if initial is not None:
                    el.update({"value": "{}".format(formats.localize(initial, use_l10n=True))})
            # DecimalField
            elif isinstance(field, forms.DecimalField):
                if initial is not None:
                    el.update({"value": "{}".format(formats.localize(initial, use_l10n=True))})
            # IntegerField
            elif isinstance(field, forms.IntegerField):
                el.update({"view": "text"})
                if initial is not None and initial not in ["", None]:
                    el.update({"value": "{}".format(initial)})
            # TimeField
            elif isinstance(field, forms.TimeField):
                el.update({"view": "datepicker", "type": "time", "stringResult": True, "editable": True})
                if initial is not None:
                    if isinstance(initial, six.string_types):
                        if "7.0.0" <= settings.WEBIX_VERSION < "8.0.0":
                            el.update(
                                {
                                    "value": "2020-01-01 {}".format(initial)
                                    .replace("-", ",")
                                    .replace(" ", ",")
                                    .replace(":", ",")
                                }
                            )
                        else:
                            el.update(
                                {"value": "{}".format(initial).replace("-", ",").replace(" ", ",").replace(":", ",")}
                            )
                    elif callable(initial):
                        _value = initial()
                        if not is_naive(_value):
                            _value = make_naive(_value)
                        if "7.0.0" <= settings.WEBIX_VERSION < "8.0.0":
                            el.update({"value": "2020-01-01 {}".format(_value.strftime("%H,%M"))})
                        else:
                            el.update({"value": "{}".format(_value.strftime("%H,%M"))})
                    else:
                        if not is_naive(initial):
                            initial = make_naive(initial)
                        if "7.0.0" <= settings.WEBIX_VERSION < "8.0.0":
                            el.update({"value": "2020-01-01 {}".format(initial.strftime("%H,%M"))})
                        else:
                            el.update({"value": "{}".format(initial.strftime("%H,%M"))})
            # DateField
            elif isinstance(field, forms.DateField):
                el.update({"view": "datepicker", "format": "%d/%m/%Y", "stringResult": True, "editable": True})
                if initial not in [None, ""]:
                    if isinstance(initial, six.string_types):
                        for DATE_INPUT_FORMAT in settings.DATE_INPUT_FORMATS:
                            try:
                                initial = datetime.datetime.strptime(initial, DATE_INPUT_FORMAT).date()
                            except ValueError:
                                pass
                            else:
                                break
                    if callable(initial):
                        # noinspection PyCallingNonCallable
                        initial = initial()
                    if isinstance(initial, six.string_types):
                        el.update({"value": "{}".format(initial)})
                    else:
                        el.update({"value": "{}".format(initial.strftime("%Y,%m,%d"))})
            # DateTimeField
            elif isinstance(field, forms.DateTimeField):
                el.update(
                    {
                        "view": "datepicker",
                        "format": "%d/%m/%Y %H:%i",
                        "stringResult": True,
                        "timepicker": True,
                        "editable": True,
                    }
                )
                if initial not in [None, ""]:
                    if isinstance(initial, six.string_types):
                        for DATETIME_INPUT_FORMAT in settings.DATETIME_INPUT_FORMATS:
                            try:
                                initial = datetime.datetime.strptime(initial, DATETIME_INPUT_FORMAT)
                            except ValueError:
                                pass
                            else:
                                break
                    if callable(initial):
                        # noinspection PyCallingNonCallable
                        initial = initial()
                    if not is_naive(initial):
                        initial = make_naive(initial)
                    if isinstance(initial, six.string_types):
                        el.update({"value": "{}".format(initial)})
                    else:
                        el.update({"value": "{}".format(initial.strftime("%Y,%m,%d,%H,%M"))})
            # BooleanField NullBooleanField
            elif isinstance(field, forms.NullBooleanField) or isinstance(field, forms.BooleanField):
                el.update({"view": "checkbox", "checkValue": "2", "uncheckValue": ""})
                if initial is not None:
                    if (
                        (isinstance(initial, bool) and initial)
                        or (isinstance(initial, six.string_types) and initial.lower() == "true")
                        or (isinstance(initial, six.string_types) and initial == "2")
                        or (isinstance(initial, int) and initial == 2)
                    ):
                        el.update({"value": "2"})
            # URLField
            elif isinstance(field, forms.URLField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({"value": initial})
            # SlugField
            elif isinstance(field, forms.SlugField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({"value": initial})
            # Image
            elif "image" in str(type(field)).lower():
                if initial is not None:
                    el.update({"value": None})
                el.update(
                    {
                        "view": "uploader",
                        "autosend": False,
                        "multiple": False,
                        "width": 150,
                        "height": 50,
                        "label": _("Upload new image") if not initial else _("Change image"),
                        "labelAlign": self.get_label_align(),
                        "on": {
                            "onAfterFileAdd": (
                                "(function (data) {{ "
                                "var file = data.file; "
                                "var reader = new FileReader(); "
                                "reader.onload = function(event) { "
                                " if (data.file.type.search('image')>=0) { "
                                "  $$('block_preview_" + self[name].auto_id + "').setHTML("
                                "'<img style=\"height: 100px; width: 170px;\" src=\"'+event.target.result+'\">');"
                                " } else {"
                                "  $$('block_preview_" + self[name].auto_id + "').setHTML(data.file.name); "
                                " }"
                                "}; "
                                "reader.readAsDataURL(file);"
                                "}} )"
                            )
                        },
                    }
                )
                delete_hidden = True
                if initial:
                    img_small = get_thumbnail(initial, "150x100", quality=85)
                    img_big = get_thumbnail(initial, "500x400", quality=85)
                    key = randint(1, 100000)
                    _template_file = "<img src=\"{}\"  onclick=\"image_modal('{}',{},{},'{}')\">".format(
                        img_small.url, img_big.url, 500, 400, str(key)
                    )
                    delete_hidden = False
                else:
                    _template_file = ""

                elements.update(
                    {
                        "{}_block".format(self[name].html_name): {
                            "id": "block_" + self[name].auto_id,
                            "label": label,  # used for tabular inline header
                            "cols": [
                                {
                                    "name_label": name,
                                    "id_label": "label_" + name,
                                    "id": "block_label_" + self[name].auto_id,
                                    "borderless": True,
                                    "template": label,
                                    "labelVisibility": {"tabular": False},
                                    "height": 30,
                                    "width": self.get_label_width(),
                                    # attenzione qui non funziona il labelAlign perche non è un input ma è un template
                                    "css": {
                                        "background-color": "transparent !important",
                                        "text-align": self.get_label_align(),
                                    },
                                },
                                {
                                    "name_label": name,
                                    "id_label": "preview_" + self[name].auto_id,
                                    "id": "block_preview_" + self[name].auto_id,
                                    "borderless": True,
                                    "view": "template",
                                    "template": _template_file,
                                    "height": 100,
                                    "width": 170,
                                },
                                {
                                    "id": self[name].auto_id + "_button_block",
                                    "width": 150,
                                    "height": 100,
                                    "rows": [
                                        el,
                                        {
                                            "cols": [
                                                {
                                                    "id": self[name].auto_id + "_download",
                                                    "view": "button",
                                                    "type": "icon",
                                                    "icon": "fas fa-download",
                                                    "tooltip": "{}".format(
                                                        os.path.basename(initial.name) if initial else ""
                                                    ),
                                                    "width": 75,
                                                    "height": 50,
                                                    "css": "webix_primary",
                                                    "hidden": delete_hidden,
                                                    "on": {
                                                        "onItemClick": (
                                                            "(function (id, e) {{ "
                                                            "window.open('{url}','_blank') "
                                                            "}})"
                                                        ).format(
                                                            url=(
                                                                initial.url
                                                                if initial
                                                                and not isinstance(initial, six.string_types)
                                                                else str(initial)
                                                            )
                                                        )
                                                    },
                                                },
                                                {
                                                    "id": self[name].auto_id + "_clean",
                                                    "name": self.add_prefix(name) + "_clean",
                                                    "view": "toggle",
                                                    "type": "icon",
                                                    "offIcon": "fas fa-trash-alt",
                                                    "onIcon": "fas fa-trash-alt",
                                                    "offLabel": "",
                                                    "onLabel": _("Deleted"),
                                                    "tooltip": "{}".format(
                                                        os.path.basename(initial.name) if initial else ""
                                                    ),
                                                    "width": 75,
                                                    "height": 50,
                                                    "css": "webix_danger",
                                                    "hidden": delete_hidden,
                                                    "click": "delete_attachment('block_{}', '{}_clean')".format(
                                                        self[name].auto_id, self[name].auto_id
                                                    ),
                                                },
                                            ]
                                        },
                                    ],
                                },
                                {"borderless": True, "template": "", "height": 30},
                            ],
                        }
                    }
                )
                _pass = True
            # FileField
            elif isinstance(field, forms.FileField):
                if initial is not None:
                    el.update({"value": None})
                el.update(
                    {
                        "view": "uploader",
                        "autosend": False,
                        "multiple": False,
                        "directory": False,
                        "width": 150,
                        "heigth": 40,
                        "label": _("Upload file") if not initial else _("Change file"),
                        "on": {
                            "onAfterFileAdd": (
                                "(function (data) {{ "
                                "if ($$('block_name_" + self[name].auto_id + "')!=undefined){"
                                "$$('block_name_" + self[name].auto_id + "').setHTML(data.file.name);"
                                "}}} )"
                            )
                        },
                    }
                )
                if isinstance(field.widget, forms.widgets.FileInput):
                    directory = field.widget.attrs.get("directory", False)
                    multiple = (field.widget.attrs.get("multiple", False),)

                    el.update(
                        {
                            "multiple": field.widget.attrs.get("multiple", False),
                            "directory": field.widget.attrs.get("directory", False),
                        }
                    )

                    if directory:
                        el.update({"label": _("Upload folder") if not initial else _("Change folder")})
                    elif multiple and not directory:
                        el.update({"label": _("Upload files") if not initial else _("Change files")})

                delete_hidden = True
                if initial:
                    delete_hidden = False

                _data = {
                    "id": "block_" + self[name].auto_id,
                    "label": label,  # used for tabular inline header
                    "cols": [
                        {
                            "height": 80,
                            "width": self.get_label_width(),
                            "labelVisibility": {"tabular": False},
                            "rows": [
                                {
                                    "name_label": name,
                                    "id_label": name,
                                    "id": "block_label_" + self[name].auto_id,
                                    "borderless": True,
                                    "template": label,
                                    "height": 40,
                                    # attention labelAlign here not works because input is not a template
                                    "css": {
                                        "background-color": "transparent !important",
                                        "text-align": self.get_label_align(),
                                    },
                                },
                                {
                                    "name_label": name,
                                    "id_label": name,
                                    "id": "block_name_" + self[name].auto_id,
                                    "borderless": True,
                                    "view": "template",
                                    "template": "{}".format(os.path.basename(initial.name) if initial else ""),
                                    "height": 40,
                                    # attention labelAlign here not works because input is not a template
                                    "css": {
                                        "background-color": "transparent !important",
                                        "color": "blue",
                                        "text-align": self.get_label_align(),
                                    },
                                },
                            ],
                        },
                        {
                            "height": 80,
                            "rows": [
                                el,
                                {
                                    "height": 40,
                                    "cols": [
                                        {
                                            "id": self[name].auto_id + "_download",
                                            "name_label": name,
                                            "id_label": name,
                                            "borderless": True,
                                            "view": "button",
                                            "type": "icon",
                                            "icon": "fas fa-download",
                                            "tooltip": "{}".format(os.path.basename(initial.name) if initial else ""),
                                            "css": "webix_primary",
                                            "hidden": delete_hidden,
                                            "width": 75,
                                            "height": 40,
                                            "on": {
                                                "onItemClick": (
                                                    "(function (id, e) {{ " "window.open('{url}','_blank') " "}})"
                                                ).format(
                                                    url=(
                                                        initial.url
                                                        if initial and not isinstance(initial, six.string_types)
                                                        else str(initial)
                                                    )
                                                )
                                            },
                                        },
                                        {
                                            "id": self[name].auto_id + "_clean",
                                            "name": self.add_prefix(name) + "_clean",
                                            "view": "toggle",
                                            "type": "icon",
                                            "offIcon": "fas fa-trash-alt",
                                            "onIcon": "fas fa-trash-alt",
                                            "offLabel": "",
                                            "onLabel": _("Deleted"),
                                            "tooltip": "{}".format(os.path.basename(initial.name) if initial else ""),
                                            "width": 75,
                                            "height": 40,
                                            "css": "webix_danger",
                                            "hidden": delete_hidden,
                                            "click": "delete_attachment('block_{}', '{}_clean')".format(
                                                self[name].auto_id, self[name].auto_id
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                        {"borderless": True, "template": "", "height": 30},
                    ],
                }
                elements.update({"{}_block".format(self[name].html_name): _data})

                _pass = True
            # FilePathFied
            elif isinstance(field, forms.FilePathField):
                # el.update({'view':''})
                if initial is not None:
                    el.update({"value": initial})
            # ModelMultipleChoiceField
            elif type(field) is forms.models.ModelMultipleChoiceField:
                if settings.WEBIX_LICENSE != "PRO":
                    raise ImproperlyConfigured(_("MultipleChoiceField is available only with PRO webix license"))
                if initial is not None:
                    el.update(
                        {
                            "value": ",".join(
                                [
                                    (
                                        str(getattr(i, field.to_field_name or "pk"))
                                        if isinstance(i, models.Model)
                                        else str(i)
                                    )
                                    for i in initial
                                ]
                            )
                        }
                    )

                if name not in self.autocomplete_fields and name not in self.autocomplete_fields_exclude:
                    count = field.queryset.only(field.queryset.model._meta.pk.name).count()
                    if count > self.min_count_suggest:
                        self.autocomplete_fields.append(name)

                # autocomplete url
                if name in self.autocomplete_fields and name not in self.autocomplete_fields_urls:
                    self.autocomplete_fields_urls.update(
                        {
                            name: self._get_url_suggest(
                                field.queryset.model._meta.app_label,
                                field.queryset.model._meta.model_name,
                                field.to_field_name,
                                field.get_limit_choices_to(),
                            )
                        }
                    )

                # autocomplete field
                if name in self.autocomplete_fields:
                    el.update(
                        {
                            "view": "multicombo",
                            "placeholder": _("Write and select"),
                            "suggest": {
                                "view": "checksuggest",
                                "selectAll": True,
                                "keyPressTimeout": 400,
                                "body": {"data": [], "dataFeed": self.autocomplete_fields_urls[name]},
                            },
                        }
                    )
                    if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                        el["suggest"]["fitMaster"] = False
                        el["suggest"]["width"] = self.get_suggest_width()

                    _vals = []
                    if "value" in el:
                        _vals = el["value"].split(",")
                    for _val in [i for i in _vals if i != "".strip()]:
                        try:
                            record = field.queryset.get(**{field.to_field_name or "pk": _val})
                        except field.queryset.model.DoesNotExist as e:
                            raise ValueError(str(e))
                        el["suggest"]["body"]["data"].append(
                            {
                                "id": "{}".format(getattr(record, field.to_field_name or "pk")),
                                "value": "{}".format(record),
                            }
                        )

                # regular field without autocomplete
                else:
                    el.update(
                        {
                            "view": "multicombo",
                            "placeholder": _("Write and select"),
                            "suggest": {
                                "view": "checksuggest",
                                "selectAll": True,
                                "keyPressTimeout": 400,
                                "body": {
                                    "data": self._add_null_choice(
                                        [
                                            {
                                                "id": "{}".format(getattr(i, field.to_field_name or "pk")),
                                                "value": "{}".format(i),
                                            }
                                            for i in field.queryset
                                        ]
                                    )
                                },
                            },
                        }
                    )
                    if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                        el["suggest"]["fitMaster"] = False
                        el["suggest"]["width"] = self.get_suggest_width()

                    # Default if is required and there are only one option
                    if callable(field.choices):
                        _choices = list(field.choices())
                    else:
                        _choices = list(field.choices)
                    if field.required and initial is None and len(_choices) == 1:
                        el.update({"value": "{}".format(_choices[0][0])})
            # ModelChoiceField
            elif isinstance(field, forms.models.ModelChoiceField):
                if initial not in [None, ""]:
                    el.update(
                        {
                            "value": (
                                str(getattr(initial, field.to_field_name or "pk"))
                                if isinstance(initial, models.Model)
                                else str(initial)
                            )
                        }
                    )
                    # add initial value with text for other purpose
                    record = field.queryset.get(**{field.to_field_name or "pk": el["value"]})
                    el["initial"] = {
                        "id": "{}".format(getattr(record, field.to_field_name or "pk")),
                        "value": "{}".format(record),
                    }

                if name not in self.autocomplete_fields and name not in self.autocomplete_fields_exclude:
                    count = field.queryset.only(field.queryset.model._meta.pk.name).count()
                    if count > self.min_count_suggest:
                        self.autocomplete_fields.append(name)

                # autocomplete url
                if name in self.autocomplete_fields and name not in self.autocomplete_fields_urls:
                    self.autocomplete_fields_urls.update(
                        {
                            name: self._get_url_suggest(
                                field.queryset.model._meta.app_label,
                                field.queryset.model._meta.model_name,
                                field.to_field_name,
                                field.get_limit_choices_to(),
                            )
                        }
                    )

                if name in self.autocomplete_fields:
                    el.update(
                        {
                            "view": "combo",
                            "placeholder": _("Write and select"),
                            "suggest": {
                                "view": "suggest",
                                "keyPressTimeout": 400,
                                "body": {"data": [], "dataFeed": self.autocomplete_fields_urls[name]},
                            },
                        }
                    )
                    if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                        el["suggest"]["fitMaster"] = False
                        el["suggest"]["width"] = self.get_suggest_width()

                    if "value" in el and el["value"] != "":  # and int(el['value']) > 0:
                        try:
                            record = field.queryset.get(**{field.to_field_name or "pk": el["value"]})
                        except field.queryset.model.DoesNotExist as e:
                            raise ValueError(str(e))
                        el["suggest"]["body"]["data"] = [
                            {
                                "id": "{}".format(getattr(record, field.to_field_name or "pk")),
                                "value": "{}".format(record),
                            }
                        ]
                else:
                    choices = self._add_null_choice(
                        [
                            {"id": "{}".format(getattr(i, field.to_field_name or "pk")), "value": "{}".format(i)}
                            for i in field.queryset
                        ]
                    )
                    if not field.required:
                        choices.insert(0, {"id": "", "value": "------", "$empty": True})
                    count = len(choices)

                    # regular field without autocomplete
                    if count <= 6:
                        el.update(
                            {
                                "view": "richselect",
                                "placeholder": _("Click and select"),
                                "suggest": {
                                    "view": "suggest",
                                    "keyPressTimeout": 400,
                                    "body": {
                                        "data": choices,
                                    },
                                },
                            }
                        )
                        if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                            el["suggest"]["fitMaster"] = False
                            el["suggest"]["width"] = self.get_suggest_width()

                        # Default if is required and there are only one option
                        if field.required and initial is None and count == 1:
                            #  TODO attenzione da rivedere perche puo dare problemi su inlines
                            el.update(
                                {"value": "{}".format(getattr(field.queryset.first(), field.to_field_name or "pk"))}
                            )
                    else:
                        el.update(
                            {
                                "view": "combo",
                                "placeholder": _("Write and select"),  # scrivi e seleziona
                                "suggest": {
                                    "view": "suggest",
                                    "keyPressTimeout": 400,
                                    "body": {
                                        "data": choices,
                                    },
                                },
                            }
                        )
                        if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                            el["suggest"]["fitMaster"] = False
                            el["suggest"]["width"] = self.get_suggest_width()

            # TypedChoiceField ChoiceField
            elif isinstance(field, forms.TypedChoiceField) or isinstance(field, forms.ChoiceField):
                choices = self._add_null_choice(
                    [{"id": "{}".format(key), "value": "{}".format(value)} for key, value in field._choices]
                )
                if not field.required:
                    choices.insert(0, {"id": "", "value": "------", "$empty": True})
                el.update(
                    {
                        "view": "richselect",
                        "placeholder": _("Click and select"),
                        "suggest": {
                            "view": "suggest",
                            "keyPressTimeout": 400,
                            "body": {
                                "data": choices,
                            },
                        },
                    }
                )
                if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                    el["suggest"]["fitMaster"] = False
                    el["suggest"]["width"] = self.get_suggest_width()

                if initial is not None:
                    el.update({"value": initial})
                # Default if is required and there are only one option
                if callable(field.choices):
                    _choices = list(field.choices())
                else:
                    _choices = list(field.choices)
                if field.required and initial is None and len(_choices) == 1:
                    el.update({"value": "{}".format(_choices[0][0])})
            # JSONField (postgresql)
            elif connection.vendor == "postgresql" and isinstance(field, JSONField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    el.update({"view": "textarea"})
                if initial is not None:
                    _value = initial
                    if callable(initial):
                        _value = initial()
                    el.update({"value": dumps(_value)})
            # SimpleArrayField (postgresql)
            elif (
                connection.vendor == "postgresql"
                and SimpleArrayField is not None
                and isinstance(field, SimpleArrayField)
            ):
                if hasattr(field, "base_field") and isinstance(field.base_field, forms.fields.DateField):
                    el.update(
                        {
                            "view": "datepicker",
                            "multiselect": "touch",
                            # "format": "%d/%m/%Y",
                            "stringResult": True,
                        }
                    )
                    if initial is not None:
                        if isinstance(initial, list):
                            el.update(
                                {
                                    "value": ", ".join([i.strftime("%Y-%m-%d") for i in initial]),
                                    "orig_value": ", ".join([i.strftime("%Y-%m-%d") for i in initial]),
                                }
                            )
                elif (
                    hasattr(field, "base_field")
                    and isinstance(field.base_field, forms.fields.TypedChoiceField)
                    and hasattr(field.base_field, "choices")
                ):
                    if callable(field.base_field.choices):
                        _choices = list(field.base_field.choices())
                    else:
                        _choices = list(field.base_field.choices)

                    el.update(
                        {
                            "view": "multicombo",
                            "placeholder": _("Write and select"),
                            "suggest": {
                                "view": "checksuggest",
                                "selectAll": True,
                                "keyPressTimeout": 400,
                                "body": {
                                    "data": self._add_null_choice(
                                        [{"id": "{}".format(k), "value": "{}".format(v)} for k, v in _choices]
                                    )
                                },
                            },
                        }
                    )
                    if self.get_suggest_width() is not None and isinstance(self.get_suggest_width(), int):
                        el["suggest"]["fitMaster"] = False
                        el["suggest"]["width"] = self.get_suggest_width()

                    if initial is not None:
                        el.update(
                            {
                                "value": (
                                    ",".join([str(i.pk) if isinstance(i, models.Model) else str(i) for i in initial])
                                    if isinstance(initial, list)
                                    else initial
                                )
                            }
                        )

                elif initial is not None:
                    el.update({"value": initial})
            # phonenumber_field PhoneNumberField
            elif PhoneNumberField is not None and isinstance(field, PhoneNumberField):
                if initial is not None and hasattr(initial, "as_e164"):
                    el.update({"value": initial.as_e164})
            # CharField
            elif isinstance(field, forms.CharField):
                if isinstance(field.widget, forms.widgets.Textarea):
                    el.update({"view": "textarea"})
                if initial is not None:
                    el.update({"value": initial})
            # GeoFields
            elif GeometryField is not None and isinstance(field, GeometryField):
                el.update({"hidden": True, "view": "textarea"})
                if initial is not None:
                    if issubclass(GEOSGeometry, django.contrib.gis.geos.GEOSGeometry) and isinstance(
                        initial, GEOSGeometry
                    ):
                        el.update({"value": initial.ewkt})
                    elif type(initial) is str:
                        el.update({"value": str(initial)})
                    else:
                        raise Exception(_("Initial value {} for geo field {} is not supported").format(initial, field))

                if apps.is_installed("django_webix_leaflet"):
                    if hasattr(self, "instance") and self.instance.pk is not None:
                        object_pk = self.instance.pk
                    else:
                        object_pk = None

                    model = self.get_model()
                    if model is not None:
                        if hasattr(self, "get_layers"):
                            # nel WebixModelForm puo essere definita get_layers specifica
                            layers = self.get_layers(name)  # name is geo field name
                        else:
                            # altrimenti usa get_layers generica perchè non conosce la definzione della view
                            layers = get_layers(model, getattr(self, "qxs_layers", None))
                        if getattr(self.instance, name, None) is None:
                            _mode = "draw"
                        else:
                            _mode = "edit"
                    else:
                        layers = []
                        _mode = "draw"

                    _row_1 = [
                        {
                            "id": self[name].auto_id + "_layer",
                            "name": self.add_prefix(name) + "_layer",
                            "label": label,
                            "labelWidth": self.get_label_width(),
                            "labelAlign": self.get_label_align(),
                            "labelVisibility": {"tabular": False},
                            "view": "select",
                            "options": [{"id": _layer["qxsname"], "value": _layer["layername"]} for _layer in layers],
                        },
                        {
                            "id": self[name].auto_id + "_editbtn",
                            "name": self.add_prefix(name) + "_editbtn",
                            "view": "button",
                            "value": _("Edit"),
                            "width": 70,
                            "on": {
                                "onItemClick": "(function (id, e) {{ $$('map').goToWebgisPk($$('{layer_selector}').getValue(),'{pk_field_name}', {object_pk}, '{mode}', '{field_name}') }})".format(  # noqa: E501
                                    layer_selector=self[name].auto_id + "_layer",
                                    pk_field_name=model._meta.pk.name,
                                    object_pk="'{}'".format(object_pk) if object_pk is not None else "undefined",
                                    mode=_mode,
                                    field_name=self[name].auto_id,
                                )
                            },
                        },
                        # {
                        #     "id": self[name].auto_id + '_cp',
                        #     "name": self.add_prefix(name) + '_cp',
                        #     'borderless': True,
                        #     "view": "template",
                        #     'template': '<div title="{}">
                        #   <i style="cursor:pointer" class="webix_icon far fa-copy"></i></div>'.format(_('Copy wkt')),
                        #     'width': 40,
                        #     "on": {
                        #         "onItemClick": "(function (id, e) {{
                        #         navigator.clipboard.writeText($$('{geo_field}').getValue()); }})".format(
                        #             geo_field=self[name].auto_id
                        #         )
                        #     },
                        # },
                        # {
                        #     "id": self[name].auto_id + '_rm',
                        #     "name": self.add_prefix(name) + '_rm',
                        #     'borderless': True,
                        #     "view": "template",
                        #     'template': '<div title="{}">
                        #     <i style="cursor:pointer" class="webix_icon far fa-trash-alt"></i>
                        #     </div>'.format(_('Empty geometry')),
                        #     'width': 40,
                        #     "on": {
                        #         "onItemClick": "(function (id, e) {{ $$('{geo_field}').setValue(''); }})".format(
                        #             geo_field=self[name].auto_id
                        #         )
                        #     }
                        # },
                        el,
                    ]
                    # _row_2 = []
                    # if PointField is not None and isinstance(field, PointField):# point
                    #     _row_2 = [
                    #         {
                    #             'width': self.get_label_width()
                    #         },
                    #         {
                    #             'id': self[name].auto_id + '_srid',
                    #             'name': self.add_prefix(name) + '_srid',
                    #             'label': 'SRID',
                    #             "view": "text",
                    #             "labelWidth": 40,
                    #             "width": 100,
                    #             "on": {
                    #                 "onChange": "(function (newv, oldv) {{
                    #                 update_geo_ewkt_point('{geo_field_selector}'); }})".format(
                    #                     geo_field_selector=self[name].auto_id,
                    #                 )
                    #             }
                    #         },
                    #         {
                    #             "id": self[name].auto_id + '_long',
                    #             "name": self.add_prefix(name) + '_long',
                    #             "label": "Long.",
                    #             "view": "text",
                    #             "labelWidth": 16,
                    #             "width": 140,
                    #             "on": {
                    #                 "onChange": "(function (newv, oldv) {{
                    #                 update_geo_ewkt_point('{geo_field_selector}'); }})".format(
                    #                     geo_field_selector=self[name].auto_id,
                    #                 )
                    #             }
                    #         },
                    #         {
                    #             "id": self[name].auto_id + '_lat',
                    #             "name": self.add_prefix(name) + '_lat',
                    #             "label": "Lat.",
                    #             "view": "text",
                    #             "labelWidth": 16,
                    #             "width": 140,
                    #             "on": {
                    #                 "onChange": "(function (newv, oldv) {{
                    #                 update_geo_ewkt_point('{geo_field_selector}'); }})".format(
                    #                     geo_field_selector=self[name].auto_id,
                    #                 )
                    #             }
                    #         },
                    #     {}
                    #     ]
                    # elif (LineStringField is not None and isinstance(field, LineStringField)) or \
                    #     (MultiLineStringField is not None and isinstance(field, MultiLineStringField)):
                    #     _row_2 = [
                    #         {
                    #             'width': self.get_label_width()
                    #         },
                    #         {
                    #             'id': self[name].auto_id + '_elements',
                    #             'name': self.add_prefix(name) + '_elements',
                    #             'label': _('N.elements'),
                    #             "view": "text",
                    #             "labelWidth": 40,
                    #             "width": 100
                    #         },
                    #         {
                    #             'id': self[name].auto_id + '_area',
                    #             'name': self.add_prefix(name) + '_area',
                    #             'label': _('Area'),
                    #             "view": "text",
                    #             "labelWidth": 40,
                    #             "width": 100
                    #         },
                    #         {
                    #             'id': self[name].auto_id + '_perimeter',
                    #             'name': self.add_prefix(name) + '_perimeter',
                    #             'label': _('Perimeter'),
                    #             "view": "text",
                    #             "labelWidth": 40,
                    #             "width": 100
                    #         },
                    #         {}
                    #     ]
                    # elif (PolygonField is not None and isinstance(field, PolygonField)) or \
                    #     (MultiPolygonField is not None and isinstance(field, MultiPolygonField)):
                    #     _row_2 = [
                    #         {
                    #             'width': self.get_label_width()
                    #         },
                    #         {
                    #             'id': self[name].auto_id + '_lenght',
                    #             'name': self.add_prefix(name) + '_lenght',
                    #             'label': _('Lenght'),
                    #             "view": "text",
                    #             "labelWidth": 40,
                    #             "width": 100
                    #         },
                    #         {}
                    #     ]
                    elements.update(
                        {
                            "{}_block".format(self[name].html_name): {
                                "id": "block_" + self[name].auto_id,
                                "label": label,  # used for tabular inline header
                                "rows": [
                                    {"cols": _row_1},
                                    #     {'cols': _row_2},
                                ],
                            }
                        }
                    )

            # InlineForeignKey
            elif isinstance(field, forms.models.InlineForeignKeyField):
                pass
            # Field not supported
            else:
                raise Exception(_("Type of field {} not supported").format(field))

            # Widget RadioSelect
            if isinstance(field.widget, forms.RadioSelect):
                _choices = field.choices if hasattr(field, "choices") else field.widget.choices
                if callable(_choices):
                    _choices = _choices()

                el.update({"view": "radio", "options": [{"id": key, "value": value} for key, value in list(_choices)]})
                if initial is not None:
                    el.update({"value": initial})
                # Default if is required and there are only one option
                if field.required and initial is None and len(list(_choices)) == 1:
                    el.update({"value": "{}".format(_choices[0][0])})

            # Widget RadioSelect
            if isinstance(field.widget, forms.PasswordInput):
                el.update({"type": "password", "view": "search", "icon": "fas fa-eye"})

            # Widget Hidden Fields
            if isinstance(field.widget, forms.HiddenInput):
                el.update({"hidden": True})

            # Delete checkbox hidden
            if self.add_prefix(name).endswith("-DELETE"):
                el.update({"hidden": True})
                elements.update(
                    {
                        "{}-icon".format(self.add_prefix(name)): {
                            "view": "button",
                            "type": "icon",
                            "icon": "far fa-trash-alt",
                            "align": "center",
                            "width": 28,
                            "hidden": not (
                                self.has_delete_permission is not None and self.has_delete_permission is True
                            ),
                            "id": "{}-icon".format(self.add_prefix(name)),
                        }
                    }
                )

            if not _pass:
                elements.update({self.add_prefix(name): el})

        return elements

    @property
    def get_tabular_fields_header(self):
        """Returns the header for the tabular inlines as webix js format"""

        fields_header = OrderedDict()
        # for name, f in self.fields.items():
        for field_name, f in self.get_elements.items():

            _field_header = None

            if "hidden" not in f or "hidden" in f and not f["hidden"]:

                _field_header = {}

                if field_name.endswith("-DELETE") or field_name.endswith("-DELETE-icon"):
                    _field_header = {"header": "", "width": 28}
                else:
                    if "width" in f:
                        _field_header.update({"width": f["width"]})
                    else:
                        _field_header.update({"fillspace": True})

                if "header" in f:
                    if not isinstance(f["header"], list):
                        f["header"] = [f["header"]]
                    _field_header.update({"header": f["header"]})
                elif "label" in f:
                    _field_header.update({"header": force_str(f["label"])})

                if (
                    _field_header is not None
                    and "header" in _field_header
                    and isinstance(_field_header["header"], str)
                    and _field_header["header"].endswith(self.help_text_template)
                ):
                    _field_header["header"] = _field_header["header"].removesuffix(self.help_text_template)

                if _field_header is not None:
                    _field_header.update({"id": "id_header_{}".format(field_name)})
                    fields_header.update({field_name: _field_header})

        return fields_header

    @property
    def get_tabular_header(self):
        """Returns the header for the tabular inlines as webix js format"""
        return dumps(
            {
                "id": self.add_prefix("datatable"),
                "view": "datatable",
                "scroll": "false",
                "autoheight": "false",
                "data": [],
                "columns": list(self.get_tabular_fields_header.values()),
            },
            cls=DjangoJSONEncoder,
        )

    def as_webix(self):
        """Webix js format form structure"""

        return dumps(list(self.get_fieldsets()), cls=DjangoJSONEncoder)[1:-1]

    def get_fieldsets(self, **kwargs):
        """Returns a dict with all the fields"""

        def _hide_elements(el, visibility_key):
            if "labelVisibility" in el and not el["labelVisibility"].get(visibility_key, True):
                if "label" in el:
                    el["label"] = ""
                    el["labelWidth"] = 0
                elif "template" in el:
                    # foto and file block use bare template as label
                    el["template"] = ""
                    el["width"] = 0
                elif "cols" in el:
                    el["cols"] = []
                    el["width"] = 0
                elif "rows" in el:
                    el["rows"] = []
                    el["width"] = 0
                else:
                    raise Exception(
                        "Django-webix form block labelVisibility configured in element "
                        "without label or template to hide"
                    )
            elif "cols" in el:
                for col in el["cols"]:
                    _hide_elements(col, visibility_key)
            elif "rows" in el:
                for row in el["rows"]:
                    _hide_elements(row, visibility_key)

        if "fs" in kwargs and kwargs["fs"] is not None:
            fs = kwargs["fs"]
        else:
            fs = self.get_elements

        if self.style == "tabular":
            for field in fs:
                fs[field]["label"] = ""
                fs[field]["labelWidth"] = 0
                if field.endswith("_block"):
                    _hide_elements(fs[field], self.style)

        return fs.values()


class BaseWebixForm(forms.BaseForm, BaseWebixMixin):

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        field_order=None,
        use_required_attribute=None,
        renderer=None,
        request=None,
        inline_id=None,
        has_add_permission=None,
        has_change_permission=None,
        has_delete_permission=None,
        parent_model=None,
        **kwparams
    ):

        # Set default parameter
        self.readonly_fields = []
        self.autocomplete_fields = []
        self.autocomplete_fields_exclude = []
        self.autocomplete_fields_urls = {}

        # Set request
        self.request = request
        self.parent_model = parent_model
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

        if getattr(self, "qxs_layers", None) is None and "qxs_layers" in kwparams:
            self.qxs_layers = kwparams.get("qxs_layers")

        super(BaseWebixForm, self).__init__(
            data,
            files,
            auto_id,
            prefix,
            initial,
            error_class,
            label_suffix,
            empty_permitted,
            field_order,
            use_required_attribute,
            renderer,
        )

        if not hasattr(self, "fields_orig"):
            self.fields_orig = copy.deepcopy(self.fields)
        for field in self.fields:
            if hasattr(self.fields[field], "queryset") and hasattr(
                self.fields_orig[field].queryset.model.objects, "get_filter"
            ):
                self.fields[field].queryset = self.fields_orig[field].queryset.filter(
                    self.fields_orig[field].queryset.model.objects.get_filter()
                )

        # Set localization fields
        if settings.USE_L10N is True:
            for field in self.fields:
                self.fields[field].localize = True
                self.fields[field].widget.is_localized = True

        # TODO: check if it works with all field types on create and update action
        self.set_readonly_fields()

    def clean(self):
        cleaned_data = super(BaseWebixForm, self).clean()
        cleaned_data = self.webix_extra_clean(cleaned_data)
        return cleaned_data


class BaseWebixModelForm(forms.BaseModelForm, BaseWebixMixin):

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,
        request=None,
        inline_id=None,
        has_add_permission=None,
        has_change_permission=None,
        has_delete_permission=None,
        parent_model=None,
        **kwargs
    ):

        # Set default
        self.readonly_fields = []
        self.autocomplete_fields = []
        self.autocomplete_fields_exclude = []
        self.autocomplete_fields_urls = {}

        # Set request
        self.request = request
        self.parent_model = parent_model
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

        if getattr(self, "qxs_layers", None) is None and "qxs_layers" in kwargs:
            self.qxs_layers = kwargs.get("qxs_layers")

        if django.VERSION > (2, 0):
            super(BaseWebixModelForm, self).__init__(
                data,
                files,
                auto_id,
                prefix,
                initial,
                error_class,
                label_suffix,
                empty_permitted,
                instance,
                use_required_attribute,
                renderer,
            )
        else:
            super(BaseWebixModelForm, self).__init__(
                data,
                files,
                auto_id,
                prefix,
                initial,
                error_class,
                label_suffix,
                empty_permitted,
                instance,
                use_required_attribute,
            )

        if not hasattr(self, "fields_orig"):
            self.fields_orig = copy.deepcopy(self.fields)
        for field in self.fields:
            if hasattr(self.fields[field], "queryset") and hasattr(
                self.fields_orig[field].queryset.model.objects, "get_filter"
            ):
                self.fields[field].queryset = self.fields_orig[field].queryset.filter(
                    self.fields_orig[field].queryset.model.objects.get_filter()
                )

        # Set localization fields
        if settings.USE_L10N is True:
            for field in self.fields:
                self.fields[field].localize = True
                self.fields[field].widget.is_localized = True

        # TODO: check if it works with all field types on create and update action
        self.set_readonly_fields()

    def clean(self):
        cleaned_data = super(BaseWebixModelForm, self).clean()
        cleaned_data = self.webix_extra_clean(cleaned_data)
        return cleaned_data

    def get_name(self):
        model = self.get_model()
        return capfirst(model._meta.verbose_name.strip())


class WebixForm(six.with_metaclass(DeclarativeFieldsMetaclass, BaseWebixForm)):
    pass


class WebixModelForm(six.with_metaclass(ModelFormMetaclass, BaseWebixModelForm)):
    pass
