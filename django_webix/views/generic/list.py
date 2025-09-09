from collections import OrderedDict
from copy import deepcopy

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import EmptyResultSet, FieldDoesNotExist, ImproperlyConfigured, PermissionDenied
from django.db.models import BooleanField, Case, F, ForeignKey, ManyToManyField, Value, When
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.http import Http404, JsonResponse
from django.template import Context, Template
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _
from django.views.generic import ListView
from django_webix.forms import WebixModelForm
from django_webix.utils.layers import get_model_geo_field_names
from django_webix.views import WebixUpdateView
from django_webix.views.generic.actions_groups import actions_group_export, actions_group_webgis
from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object


def get_action_dict(request, action):
    """
    Constructs a dictionary of action attributes for a given action.

    This function extracts and organizes the attributes of an action, such as its form,
    template view, and metadata, into a structured dictionary. It ensures that optional
    attributes like `form`, `template_view`, and `form_view` are set to `None` if they
    are not defined in the action.

    Args:
        request: The HTTP request object.
        action: The action object containing attributes to be extracted.

    Returns:
        dict: A dictionary containing the action's attributes, including:
            - `func`: The action function.
            - `action_key`: The unique key identifying the action.
            - `response_type`: The type of response expected from the action.
            - `allowed_permissions`: Permissions required to execute the action.
            - `short_description`: A brief description of the action.
            - `modal_header`, `modal_title`, `modal_click`, `modal_ok`, `modal_cancel`: Modal dialog attributes.
            - `form`: The form associated with the action, if any.
            - `reload_list`: Whether to reload the list after executing the action.
            - `template_view`: The template view for the action, if any.
            - `dynamic`: Whether the action is dynamic.
            - `form_view_template`: The template for the form view, if any.
            - `form_view`: The form view for the action, if any.
            - `group`: The group the action belongs to.
            - `icon`: The icon associated with the action.
    """
    # needed to set var with None as value
    form = action.form(request=request) if hasattr(action, "form") and action.form is not None else None
    template_view = (
        action.template_view if hasattr(action, "template_view") and action.template_view is not None else None
    )
    form_view = action.form_view if hasattr(action, "form_view") and action.form_view is not None else None

    return {
        "func": action,
        "action_key": action.action_key,
        "response_type": action.response_type,
        "allowed_permissions": action.allowed_permissions,
        "short_description": action.short_description,
        "modal_header": action.modal_header,
        "modal_title": action.modal_title,
        "modal_click": action.modal_click,
        "modal_ok": action.modal_ok,
        "modal_cancel": action.modal_cancel,
        "form": form,
        "reload_list": getattr(action, "reload_list", True),
        "template_view": template_view,
        "dynamic": action.dynamic,
        "form_view_template": action.form_view_template,
        "form_view": form_view,
        "group": action.group,
        "icon": action.icon or "",
    }


def get_actions_flexport(request, model):
    """
    Retrieves and constructs Flexport-specific actions for a given model.

    This function checks if the `flexport` app is installed and if a model is provided.
    If so, it dynamically creates actions for each active `Export` instance associated
    with the model. These actions are used to trigger data extraction processes.

    Args:
        request: The HTTP request object.
        model: The Django model for which actions are being generated.

    Returns:
        list: A list of dynamically generated action functions for Flexport.
    """
    _actions = []
    # add flexport actions
    if apps.is_installed("flexport") and model is not None:
        from django.contrib.contenttypes.models import ContentType
        from flexport.models import Export
        from flexport.views import create_extraction

        model_ct = ContentType.objects.get(model=model._meta.model_name, app_label=model._meta.app_label)

        def action_builder(export_instance):
            def _action(listview, request, qs):
                return create_extraction(request, export_instance.id, qs)

            _action.__name__ = "flexport_action_%s" % export_instance.id
            _action.response_type = "blank"
            _action.short_description = export_instance.action_name
            _action.action_key = "flexport_{}".format(export_instance.id)
            _action.allowed_permissions = []
            _action.modal_header = _("Fill in the form")
            _action.modal_title = _("Are you sure you want to proceed with this action?")
            _action.modal_click = _("Go")
            _action.modal_ok = _("Proceed")
            _action.modal_cancel = _("Undo")
            _action.reload_list = False
            _action.dynamic = False
            _action.form_view_template = None
            _action.form_view = None
            _action.group = actions_group_export
            _action.icon = None
            return _action

        for export_instance in Export.objects.filter(model=model_ct, active=True):
            if export_instance.is_enabled(request):
                _actions.append(action_builder(export_instance))
    return _actions


class WebixListView(WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin, ListView):
    """
    A custom ListView for Webix integration, providing advanced features like dynamic actions,
    pagination, filtering, and JSON responses.

    This class extends Django's `ListView` and integrates with Webix to provide a rich,
    interactive list interface. It supports features such as:
    - Dynamic actions (e.g., Flexport actions).
    - Pagination and sorting.
    - JSON-based data loading and filtering.
    - Editable fields and modal forms.
    - Integration with WebGIS for geographic data visualization.
    - Customizable columns, headers, and footers.
    - Permission-based access control.

    Main attributes:
        http_method_names (list): Allowed HTTP methods (e.g., `get`, `post`).
        pk_field (str): The primary key field name.
        fields (list): List of fields to display in the table.
        order_by (str): Default ordering for the queryset.
        actions (list): List of actions available in the list view.
        enable_json_loading (bool): Whether to enable JSON-based data loading.
        template_name (str): The template used to render the list.
        title (str): The title of the list view.
        enable_column_webgis (bool): Whether to enable WebGIS column integration.
        enable_column_copy (bool): Whether to enable the copy column.
        enable_column_delete (bool): Whether to enable the delete column.
        enable_row_click (bool): Whether to enable row click actions.
        type_row_click (str): Type of row click action (`single` or `double`).
        fields_editable (list): List of fields that are editable.
    """

    # request vars
    http_method_names = ["get", "post"]  # enable POST for filter porpoise

    # queryset vars
    pk_field = None
    fields = None  # ex. [{'field_name':'XXX','datalist_column':'YYY',}]
    order_by = None

    # list operations / actions
    column_id = None
    actions = []  # [multiple_delete_action]
    adjust_row_height = False
    header_rows = 2

    errors_on_popup = False

    # paging
    enable_json_loading = False
    enable_json_choices_loading = False  # TODO: developed for future javascript client implementations
    paginate_count_default = 100
    paginate_start_default = 0
    paginate_count_key = "count"
    paginate_start_key = "start"

    # template vars
    template_name = "django_webix/generic/list.js"
    title = None
    enable_column_webgis = True
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = "single"  # or 'double'
    enable_actions = True

    fields_editable = []  # es. ['utilizzo__denominazione']

    def is_actions_flexport_enable(self, request):
        """
        Determines whether Flexport actions are enabled for the current request.

        Args:
            request: The HTTP request object.

        Returns:
            bool: `True` if Flexport actions are enabled, otherwise `False`.
        """
        return True

    def is_errors_on_popup(self, request):
        return self.errors_on_popup

    def is_installed_django_webix_filter(self):
        return apps.is_installed("django_webix.contrib.filter")

    def is_enabled_django_webix_filter(self):
        if self.is_installed_django_webix_filter() and self.model is not None:
            from django_webix.contrib.filter.utils.config import model_is_enabled

            return model_is_enabled(self.model)
        return False

    def get_header_rows(self, request):
        """
        Returns the number of header rows to display in the list view.

        Args:
            request: The HTTP request object.

        Returns:
            int: The number of header rows.
        """
        return self.header_rows

    def _optimize_select_related(self, qs):
        """
        Optimizes the queryset by adding `select_related` for foreign key relationships.

        This method analyzes the fields defined in the list view and identifies foreign key
        relationships to optimize database queries using `select_related`. This reduces the
        number of queries required to fetch related data.

        Args:
            qs (QuerySet): The initial queryset to optimize.

        Returns:
            QuerySet: The optimized queryset with `select_related` applied.
        """
        # extrapolate the information to populate `select_related`
        _select_related = []
        if self.get_fields() is not None:
            for field in self.get_fields():
                if field.get("field_name") is not None:
                    field_name = field.get("field_name")
                    _model = self.model
                    _field = None
                    _related = []
                    for name in field_name.split("__"):
                        try:
                            _field = _model._meta.get_field(name)
                            if isinstance(_field, ManyToManyField):  # Check if field is M2M
                                raise FieldDoesNotExist()
                        except FieldDoesNotExist:
                            break  # name is probably a lookup or transform such as __contains

                        if (
                            isinstance(_field, ForeignKey)
                            and hasattr(_field, "related_model")
                            and _field.related_model is not None
                        ):
                            _related.append(name)
                            _model = _field.related_model  # field is a relation
                        else:
                            break  # field is not a relation, any name that follows is probably a lookup or transform
                    _related = "__".join(_related)
                    if _related != "":
                        _select_related.append(_related)
            if _select_related:
                qs = qs.select_related(*_select_related)
        return qs

    def _model_translations(self, qs):
        """
        Applies model translations to the queryset if the `modeltranslation` app is installed.

        This method checks if any fields in the list view are translated and annotates the
        queryset to include the translated values based on the current language.

        Args:
            qs (QuerySet): The initial queryset to process.

        Returns:
            QuerySet: The queryset with translated fields annotated.
        """
        if apps.is_installed("modeltranslation"):
            from modeltranslation.fields import TranslationFieldDescriptor

            fields = [field for field in self.get_fields() or [] if field.get("field_name") is not None]
            for field in fields:
                field_name = field.get("field_name")
                _model = self.model
                _field = None
                for name in field_name.split("__"):
                    try:
                        _field = _model._meta.get_field(name)
                        if isinstance(_field, ManyToManyField):  # Check if field is M2M
                            raise FieldDoesNotExist()
                    except FieldDoesNotExist:
                        break  # name is probably a lookup or transform such as __contains
                    if hasattr(_field, "related_model") and _field.related_model is not None:
                        _model = _field.related_model  # field is a relation
                    else:
                        break  # field is not a relation, any name that follows is probably a lookup or transform

                # Check if last field of last model is translated (exclude initial model)
                if _field is not None and _model != self.model:
                    _field_attribute = getattr(_model, _field.name, None)
                    if isinstance(_field_attribute, TranslationFieldDescriptor):
                        qs = qs.annotate(
                            **{field_name: Coalesce("{}_{}".format(field_name, get_language()), field_name)}
                        )
        return qs

    def get_column_id(self, request):
        return self.column_id or "id"

    def get_adjust_row_height(self, request):
        return self.adjust_row_height

    def get_fields(self, fields=None):
        """
        Retrieves and processes the fields to be displayed in the list view.

        This method supports both static and dynamic field definitions, including
        template-based rendering for columns. It also ensures that server-side
        filtering is enabled if JSON loading is active.

        Args:
            fields (list, optional): A custom list of fields to override the default fields.

        Returns:
            list: A list of processed field definitions.

        Raises:
            Exception: If no server filter is defined when JSON loading is enabled.
        """
        if self.fields is not None:
            _in_fields = deepcopy(self.fields)
            # otherwise in the loop below the static fields attribute is redefined
            # and they don't work lazy_translations
        elif fields is not None:
            _in_fields = fields
        else:
            _in_fields = None

        if _in_fields is None:
            return None
        else:
            _fields = []
            if self.enable_json_loading:
                server_filter = False
            else:
                server_filter = None
            for _field in _in_fields:
                datalist_column = _field["datalist_column"]
                if type(datalist_column) is dict:
                    if "template_string" in datalist_column:
                        template = Template(datalist_column["template"])
                    elif "template_name" in datalist_column:
                        template = get_template(datalist_column["template_name"])
                    else:
                        raise Exception("Template is not defined")
                    context = Context(datalist_column.get("context", {}))
                else:  # string
                    template = Template(datalist_column)
                    context = Context({})
                _field["datalist_column"] = template.render(context)
                # check server into datalist_column if is json loading
                if self.enable_json_loading:
                    if "server" in _field["datalist_column"]:
                        server_filter = True
                _fields.append(_field)
            if server_filter is False:
                raise Exception("Must be at least one server filter")
            return _fields

    def get_annotations_geoavailable(self, geo_field_names):
        """
        Generates database annotations to check the availability of geographic fields.

        This method creates a dictionary of annotations for the given geographic field names.
        Each annotation adds a boolean field to the queryset indicating whether the geographic
        field contains a non-null value. This is useful for filtering or displaying only objects
        with valid geographic data.

        Args:
            geo_field_names (list): A list of geographic field names to check.

        Returns:
            dict: A dictionary of annotations where keys are field names suffixed with `_available`
                  and values are `Case` expressions that evaluate to `True` if the field is not null.
        """
        annotations = {}
        for geo_field_name in geo_field_names:
            annotations.update(
                {
                    f"{geo_field_name}_available": Case(
                        When(**{f"{geo_field_name}__isnull": False}, then=True),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                }
            )
        return annotations

    def get_initial_queryset(self):
        """
        Retrieves the initial queryset for the list view.

        This method determines the base queryset to use for the list view. It prioritizes
        the `queryset` attribute if it is explicitly set. If not, it falls back to the default
        manager of the model. If neither is available, it raises an `ImproperlyConfigured` exception.

        Returns:
            QuerySet: The initial queryset for the list view.

        Raises:
            ImproperlyConfigured: If neither `queryset` nor `model` is defined.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                (
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()."
                )
                % {"cls": self.__class__.__name__}
            )
        return queryset

    def get_queryset(self, initial_queryset=None, apply_translations=True, **kwargs):
        """
        Retrieves and processes the queryset for the list view.

        This method applies translations, filters, and optimizations (e.g., `select_related`)
        to the queryset. It also supports integration with `django_filtersmerger` and
        WebGIS annotations.

        Args:
            initial_queryset (QuerySet, optional): A custom queryset to use as the base.
            apply_translations (bool, optional): Whether to apply model translations.

        Returns:
            QuerySet: The processed queryset.
        """
        # bypass improperly configured for custom queryset without model
        if self.model:
            if initial_queryset is not None:
                qs = initial_queryset
            else:
                qs = self.get_initial_queryset()

            if apply_translations:
                qs = self._model_translations(qs)  # Check model translations

            if apps.is_installed("django_filtersmerger"):
                from django_filtersmerger import FilterMerger

                filter_merger = FilterMerger(request=self.request)
                qs = filter_merger.get_queryset(self.model, initial_queryset=qs)

            # annotate geo available
            if self.is_enable_column_webgis(self.request):
                geo_field_names = get_model_geo_field_names(self.model)
                annotations = self.get_annotations_geoavailable(geo_field_names)
                if annotations:
                    qs = qs.annotate(**annotations)

            # optimize select related queryset (only if fields are defined)
            qs = self._optimize_select_related(qs)  # TODO

            return self.apply_ordering(qs)

        return None

    def get_method_choices_filters(self, field_name):
        # usually DB distinct and order by are slower than distinct by python set
        return "distinct"  # "set" by python OR "distinct" by db query

    def get_choices_filters(self, empty=False):
        """
        Retrieves the filter choices for fields in the list view.

        This method generates a dictionary of filter choices for each field, including
        choices for boolean fields, model fields with predefined choices, and dynamic
        choices fetched from the database. It supports both simple and complex field types,
        including those from the `django_webix.contrib.extra_fields` app.

        Args:
            empty (bool, optional): If `True`, returns an empty choice as the first option.

        Returns:
            dict: A dictionary where keys are field names and values are lists of choices.
        """
        _fields_choices = {}
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get("datalist_column") is not None:
                    field_name = field.get("field_name")
                    _fields_choices[field_name] = [
                        {"id": "null", "value": "---"},
                    ]  # default add null/'' option
                    if not empty:
                        if self.model is not None:
                            try:
                                _modelfield = self.model._meta.get_field(field_name)
                            except FieldDoesNotExist:
                                _modelfield = None
                        else:
                            _modelfield = None
                        if "boolean" in str(field.get("field_type", "")).lower():
                            _fields_choices[field_name] += [
                                {"id": "true", "value": _("Yes")},
                                {"id": "false", "value": _("No")},
                            ]
                        elif _modelfield is not None and _modelfield.choices is not None:
                            _fields_choices[field_name] = [
                                {"id": i[0], "value": i[1]} for i in _modelfield.get_choices()
                            ]
                        elif (
                            apps.is_installed("django_webix.contrib.extra_fields")
                            and "extrafields" in str(field.get("field_type", "")).lower()
                        ):
                            from django.contrib.contenttypes.models import ContentType

                            content_type_id = ContentType.objects.get_for_model(self.model).pk

                            if getattr(settings, "WEBIX_EXTRA_FIELDS_ENABLE_CACHE", False):
                                from django.core.cache import cache

                                extra_fields = cache.get("django_webix_extra_fields", {})
                                if content_type_id in extra_fields:
                                    for mf in extra_fields[content_type_id]:
                                        if mf["field_name"] == field_name:
                                            if mf["has_choices"]:
                                                _fields_choices[field_name] = [
                                                    {"id": i["key"], "value": i["value"]} for i in mf["choices"]
                                                ]
                                            break

                            else:
                                from django_webix.contrib.extra_fields.models import ModelField

                                mf = ModelField.objects.filter(
                                    field_name=field_name, content_type_id=content_type_id
                                ).first()
                                if mf is not None and mf.modelfieldchoice_set.exists():
                                    options = mf.modelfieldchoice_set.values_list("key", "value")
                                    _fields_choices[field_name] = [{"id": i[0], "value": i[1]} for i in options]
                        elif (
                            "serverSelectFilter" in field.get("datalist_column")
                            or "serverRichSelectFilter" in field.get("datalist_column")
                            or "serverMultiSelectFilter" in field.get("datalist_column")
                            or "serverMultiComboFilter" in field.get("datalist_column")
                        ) and (
                            "_options" in field.get("datalist_column")
                        ):  # enable only if choices are required
                            if field.get("field_pk") is None:
                                if self.get_method_choices_filters(field_name) == "set":
                                    _fields_choices[field_name] += set(
                                        [
                                            str(i)
                                            for i in self.get_queryset()
                                            .filter(**{field_name + "__isnull": False})
                                            .values_list(field_name, flat=True)
                                        ]
                                    )
                                else:
                                    _fields_choices[field_name] += [
                                        str(i)
                                        for i in self.get_queryset()
                                        .filter(**{field_name + "__isnull": False})
                                        .values_list(field_name, flat=True)
                                        .distinct()
                                        .order_by()
                                    ]
                            else:
                                if self.get_method_choices_filters(field_name) == "set":
                                    _fields_choices[field_name] += set(
                                        [
                                            {
                                                "id": key,
                                                "value": value,
                                            }
                                            for key, value in self.get_queryset()
                                            .filter(**{field_name + "__isnull": False})
                                            .values_list(field.get("field_pk"), field_name)
                                        ]
                                    )
                                else:
                                    _fields_choices[field_name] += [
                                        {
                                            "id": key,
                                            "value": value,
                                        }
                                        for key, value in self.get_queryset()
                                        .filter(**{field_name + "__isnull": False})
                                        .values_list(field.get("field_pk"), field_name)
                                        .distinct()
                                        .order_by()
                                    ]

        return _fields_choices

    def is_enable_footer(self):
        """
        Determines whether the footer should be displayed in the list view.

        This method checks if any of the fields in the list view have a footer definition.
        If at least one field has a footer, it returns `True`, indicating that the footer
        should be rendered.

        Returns:
            bool: `True` if the footer is enabled, otherwise `False`.
        """
        is_footer = False
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get("footer") is not None:
                    is_footer = True
        return is_footer

    def get_footer(self):
        """
        Computes and returns the footer data for the list view.

        If the list view has fields with footer definitions, this method calculates the
        aggregated values (e.g., sum, average) for those fields and returns them as a dictionary.

        Returns:
            dict: A dictionary containing the footer values for each field, or `None` if no footer is defined.
        """
        if self.is_enable_footer() and self.model is not None:
            # INFO: Splitting into multiple queries makes it slower
            aggregation_dict = {}
            qs = self.get_queryset(apply_translations=False)
            pk_field_name = qs.model._meta.pk.name
            for field in self.get_fields():
                if field.get("footer") is not None:
                    aggregation_dict.update({field.get("field_name") + "_footer": field.get("footer")})
            qs = qs.only(pk_field_name).aggregate(**aggregation_dict)
            return dict(qs)
        else:
            return None

    def get_ordering(self):
        """
        Determines the ordering for the queryset based on user input or default settings.

        This method checks the request for sorting parameters (e.g., `sort[]` in POST/GET)
        and falls back to the default `order_by` attribute if no user input is provided.

        Returns:
            tuple: A tuple of field names to use for ordering the queryset.
        """
        if self.request.POST.getlist("sort[]"):
            return self.request.POST.getlist("sort[]")
        else:
            if self.order_by is not None:
                return self.order_by
            else:
                return (self.get_pk_field(),)

    def apply_ordering(self, queryset):
        order = self.get_ordering()
        return queryset.order_by(*order)

    def get_paginate_count(self):
        """
        Retrieves the number of items to display per page from the request.

        This method checks the request parameters (`count` key) for pagination settings
        and returns the value as an integer. If the value is not provided or invalid,
        it falls back to the default pagination count.

        Returns:
            int: The number of items to display per page.

        Raises:
            Exception: If the pagination count is not an integer.
        """
        paginate_count = self.request.GET.get(
            self.paginate_count_key, self.request.POST.get(self.paginate_count_key, self.paginate_count_default)
        )
        try:
            return int(paginate_count)
        except ValueError:
            raise Exception(_("Paginate count is not integer"))

    def get_paginate_start(self):
        """
        Retrieves the starting index for pagination from the request.

        This method checks the request parameters (`start` key) for the pagination start index
        and returns the value as an integer. If the value is not provided or invalid,
        it falls back to the default start index.

        Returns:
            int: The starting index for pagination.

        Raises:
            Exception: If the pagination start index is not an integer.
        """
        paginate_start = self.request.GET.get(
            self.paginate_start_key, self.request.POST.get(self.paginate_start_key, self.paginate_start_default)
        )
        try:
            return int(paginate_start)
        except ValueError:
            raise Exception(_("Paginate start is not integer"))

    def paginate_queryset(self, queryset, page_size):
        """
        Applies pagination to the queryset based on the current pagination settings.

        Args:
            queryset (QuerySet): The queryset to paginate.
            page_size (int): The number of items per page (not used in this implementation).

        Returns:
            QuerySet: A slice of the queryset representing the current page.
        """
        # page_size not used
        paginate_count = self.get_paginate_count()
        paginate_start = self.get_paginate_start()
        return queryset[paginate_start : paginate_start + paginate_count]

    def _get_objects_datatable_values(self, qs):
        """
        Extracts the values for the datatable from the queryset.

        This method processes the queryset to retrieve the values of the fields defined
        in the list view, including the primary key and any geographic availability fields.
        It also handles annotations for fields that require a custom primary key or geographic data.
        This is very important to inject the values into webix datatable for field with set queryset_exclude.

        Args:
            qs (QuerySet): The queryset from which to extract values.

        Returns:
            QuerySet: A values queryset containing the data for the datatable.
        """
        values = [self.get_pk_field()]
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get("field_name") is not None and (
                    field.get("queryset_exclude") is None or field.get("queryset_exclude") is not True
                ):
                    values.append(field["field_name"])
                    if field.get("field_pk") is not None:
                        qs = qs.annotate(**{field["field_name"]: F(field["field_pk"])})
        if self.is_enable_column_webgis(self.request):
            for field_name in get_model_geo_field_names(self.model):
                values += [f"{field_name}_available"]
        data = qs.values(
            *values, **({"id": F("pk")} if self.get_pk_field() != "id" and not hasattr(self.model, "id") else {})
        )
        return data

    def get_objects_datatable(self):
        """
        Retrieves the data for the datatable in the list view.

        This method applies filtering, ordering, and pagination to the queryset
        and returns the data in a format suitable for Webix datatable rendering.

        Returns:
            list: A list of dictionaries representing the datatable rows.
        """
        if self.model and not self.enable_json_loading:
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # raise Exception(qs)
            # pagination (applied only for json request)
            # if self.is_json_request:
            #    qs = self.paginate_queryset(qs, None)
            # build output
            if qs is not None:
                if type(qs) is list:
                    return qs
                else:  # queryset
                    # apply ordering
                    qs = self.apply_ordering(qs)
                    return self._get_objects_datatable_values(qs)
        return None

    def filters_objects_datatable(self, qs):
        """
        Filters the queryset or list based on the IDs provided in the request.

        This method checks the request for a comma-separated list of IDs and filters the
        queryset or list to include only those objects.

        Args:
            qs (QuerySet or list): The queryset or list to filter.

        Returns:
            QuerySet or list: The filtered queryset or list.
        """
        ids = self.request.POST.get("ids", "").split(",")
        ids = list(set(ids) - {None, ""})

        if len(ids) > 0:
            if type(qs) is list:
                for item in qs:
                    if item.get("id") not in ids:
                        qs.remove(item)
            elif self.model is not None:
                auto_field_name = self.model._meta.get_field(self.get_pk_field()).name
                qs = qs.filter(**{auto_field_name + "__in": ids})
        return qs

    def get_pk_field(self):
        """
        Retrieves the name of the primary key field for the model.

        If `pk_field` is explicitly set, it returns that value. Otherwise, it defaults to "id".

        Returns:
            str: The name of the primary key field.
        """
        if self.pk_field is not None:
            return self.pk_field
        return "id"

    # ########## TEMPLATE BUILDER ###########

    def _get_action_dict(self, action):
        return get_action_dict(self.request, action)

    def _get_actions_flexport(self, request):
        if self.is_actions_flexport_enable(request=request):
            return get_actions_flexport(request, self.model)
        else:
            return []

    def get_actions(self):
        """
        Retrieves all actions available in the list view, including Flexport actions.

        This method combines the default actions with dynamically generated Flexport actions
        and returns them as a dictionary, where keys are action keys and values are action
        metadata.

        Returns:
            dict: A dictionary of actions, where each key is an action key and the value is
                  a dictionary of action attributes.
        """
        _actions = deepcopy(self.actions)
        _actions += self._get_actions_flexport(request=self.request)

        _dict_actions = {}
        for _action in _actions:
            _dict_actions[_action.action_key] = self._get_action_dict(_action)
        return _dict_actions

    def get_actions_menu_grouped(self):
        """
        Groups actions into a menu structure for the Webix interface.

        This method organizes actions into groups and submenus, including default actions
        and WebGIS-related actions. It returns a list of menu items suitable for rendering
        in the Webix UI.

        Returns:
            list: A list of menu items, where each item is either an action or a group of actions.
        """
        _menus = OrderedDict()
        _no_group = []
        # default actions
        for action_key, action in self.get_actions().items():
            _action_menu = {
                "id": action_key,
                "value": action["short_description"],
                "icon": action.get("icon", ""),
            }
            if action["group"] is None:
                _no_group.append(_action_menu)
            else:
                if action["group"] in _menus:
                    _menus[action["group"]].append(_action_menu)
                else:
                    _menus[action["group"]] = [_action_menu]

        # add webgis actions
        for layer in self.get_layers(area="actions_list"):
            _layer_actions_menu = [
                {"id": "gotowebgis_" + layer["codename"], "value": _("Go to map") + " " + layer["layername"]},
                {"id": "filtertowebgis_" + layer["codename"], "value": _("Filter in map") + " " + layer["layername"]},
            ]
            if actions_group_webgis in _menus:
                _menus[actions_group_webgis] += _layer_actions_menu
            else:
                _menus[actions_group_webgis] = _layer_actions_menu

        # rebuild output for webix
        _menu_out = _no_group
        for j, (_group) in enumerate(sorted(_menus, key=lambda x: x.order), 1):
            _menu_out.append(
                {"id": j, "value": _group.name, "icon": _group.icon, "disable": "true", "submenu": _menus[_group]}
            )
        return _menu_out

    def is_enable_actions(self, request):
        return self.enable_actions

    def is_enable_column_webgis(self, request):
        return self.enable_column_webgis and apps.is_installed("django_webix_leaflet")

    def is_enable_column_copy(self, request):
        return self.enable_column_copy

    def is_enable_column_delete(self, request):
        return self.enable_column_delete

    def is_enable_row_click(self, request):
        return self.enable_row_click

    def get_type_row_click(self, request):
        return self.type_row_click

    def get_title(self):
        if self.title is not None:
            return self.title
        if self.model is not None:
            return self.model._meta.verbose_name_plural
        return None

    # ########## RESPONSE BUILDER ###########

    @property
    def is_json_request(self):
        if "json" in self.request.GET or "json" in self.request.POST:
            return True
        else:
            return False

    @property
    def is_action_request(self):
        if "action" in self.request.GET or "action" in self.request.POST:
            return True
        else:
            return False

    @property
    def is_update_request(self):
        if "update" in self.request.GET or "update" in self.request.POST:
            return True
        else:
            return False

    def is_editable(self):
        return len(self.get_fields_editable()) > 0

    def get_update_form_class(self):
        """
        Dynamically generates a form class for updating editable fields in the list view.

        This method creates a `WebixModelForm` subclass with fields corresponding to the
        editable fields defined in the list view.

        Returns:
            class: A dynamically generated form class for updating objects.
        """
        _list_view = self

        class UpdateForm(WebixModelForm):
            class Meta:
                localized_fields = "__all__"
                model = _list_view.model
                fields = [i.split("__")[0] for i in _list_view.get_fields_editable()]

        return UpdateForm

    def get_update_view(self, request, *args, **kwargs):
        """
        Creates and returns a view for handling update requests.

        This method dynamically generates a `ListUpdateView` class that handles POST requests
        for updating objects in the list view. It ensures that only users with the appropriate
        permissions can perform updates.

        Args:
            request: The HTTP request object.
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response from the update view.
        """
        kwargs.update({"pk": request.GET.get("pk", request.POST.get("pk"))})
        _list_view = self

        # TODO: is login is required depends if list has login required
        @method_decorator(login_required, name="dispatch")
        class ListUpdateView(WebixUpdateView):
            has_view_permission = _list_view.has_view_permission
            has_add_permission = _list_view.has_add_permission
            has_change_permission = _list_view.has_change_permission
            has_delete_permission = _list_view.has_delete_permission

            def get_queryset(self):
                return _list_view.get_queryset()  # this use list initial queryset

            success_url = ""  # for bypass the template exception
            http_method_names = ["post"]  # only update directly without render
            model = _list_view.model

            def get_form_class(self):
                return _list_view.get_update_form_class()

            def response_valid(self, success_url=None, **kwargs):
                return JsonResponse({"status": True})

            def response_invalid(self, success_url=None, **kwargs):
                return JsonResponse({"status": False})

        return ListUpdateView.as_view()(request, *args, **kwargs)

    def get_fields_editable(self):
        """
        Retrieves the list of editable fields for the current user.

        This method checks the user's permissions and returns the list of fields that can be
        edited in the list view. If the user lacks change permissions, it returns an empty list.

        Returns:
            list: A list of editable field names.
        """
        if self.has_change_permission(self.request, obj=None):
            return self.fields_editable
        else:
            return []

    def get_request_action(self):
        """
        Retrieves the action function associated with the current request.

        This method checks the request parameters for an `action` key and returns the
        corresponding action function from the list of available actions.

        Returns:
            function: The action function to execute.
        """
        action_name = self.request.POST.get("action", self.request.GET.get("action", None))
        return self.get_actions().get(action_name)["func"]

    def post(self, request, *args, **kwargs):  # all post works like get
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(WebixListView, self).get(request, *args, **kwargs)

    def get_total_count(self, queryset):
        """
        Computes the total number of objects in the queryset.

        This method optimizes the count operation by using `only()` to fetch only the primary
        key field if possible. For complex queries (e.g., those involving `UNION`), it falls
        back to the standard `count()` method.

        Args:
            queryset (QuerySet): The queryset to count.

        Returns:
            int: The total number of objects in the queryset.
        """
        try:
            qs_query = str(queryset.query)
        except EmptyResultSet:
            total_count = 0
        else:
            pk_field = self.get_pk_field()
            model_fields = [field.name for field in self.model._meta.get_fields()]
            if "UNION" in qs_query or pk_field not in model_fields:
                total_count = queryset.count()
            else:  # optimized count
                total_count = queryset.only(pk_field).count()
        return total_count

    def json_response(self, request, *args, **kwargs):
        """
        Generates a JSON response for the list view.

        This method handles requests for paginated data, footer data, or filter choices.
        It returns the data in a structured JSON format, including pagination metadata.

        Args:
            request: The HTTP request object.

        Returns:
            JsonResponse: A JSON response containing the requested data.
        """
        # ONLY for get_queryset() -> qs and not get_queryset() -> list

        if bool(request.GET.get("only_footer")) or bool(request.POST.get("only_footer")):
            data = {"footer": self.get_footer()}
        elif self.enable_json_choices_loading is True and (
            bool(request.GET.get("only_choices_filters")) or bool(request.POST.get("only_choices_filters"))
        ):
            data = {"choices_filters": self.get_choices_filters(empty=False)}
        else:
            _data = []
            total_count = 0
            if self.model:
                qs = self.get_queryset(initial_queryset=self.get_initial_queryset())
                # filters application (like IDS selections)
                qs = self.filters_objects_datatable(qs)
                # apply ordering
                qs = self.apply_ordering(qs)
                # total count
                total_count = self.get_total_count(qs)
                # apply pagination
                qs_paginate = self.paginate_queryset(qs, None)
                # build output
                if qs_paginate is not None:
                    if type(qs_paginate) is list:
                        raise Exception(
                            _("Json response is available only if get_queryset() return a queryset and not a list")
                        )
                    else:  # queryset
                        _data = self._get_objects_datatable_values(qs_paginate)

            pos = self.get_paginate_start()
            # output must be list and not values of queryset
            data = {
                # "footer": self.get_footer() if pos == 0 else None,  # footer is computed only for first page
                "is_enable_footer": self.is_enable_footer(),
                "count": self.get_paginate_count(),
                "total_count": total_count,
                "pos": pos,
                "data": list(_data),
            }
        return JsonResponse(data, safe=False)

    def action_response(self, request, *args, **kwargs):
        """
        Executes an action and returns the response.

        This method retrieves the action function based on the request, checks permissions,
        and executes the action on the filtered and ordered queryset.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: The response from the action function.

        Raises:
            Http404: If the action is not registered or permissions are denied.
        """
        action_function = self.get_request_action()
        if action_function is None:
            raise Http404(_("This action is not registered"))
        else:
            # check permissions
            for key in getattr(action_function, "allowed_permissions", []):
                if hasattr(self, "has_{}_permission".format(key)):
                    if getattr(self, "has_{}_permission".format(key))(request) is not True:
                        raise Http404(_("Permission denied: {}".format(key)))
                else:
                    raise Http404(_("This permission is not registered on this class"))
            # execution
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # apply ordering
            if type(qs) is not list:
                qs = self.apply_ordering(qs)
            return action_function(self, request, qs)

    def dispatch(self, *args, **kwargs):
        """
        Dispatches the request to the appropriate handler.

        This method routes the request to handle actions, JSON responses, updates,
        or standard template rendering based on the request type.

        Args:
            *args: Variable-length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The response from the appropriate handler.

        Raises:
            PermissionDenied: If the user lacks view permissions.
        """
        if not self.has_view_permission(request=self.request):
            raise PermissionDenied(_("View permission is not allowed"))
        if self.is_action_request:  # added for action response
            return self.action_response(self.request, *args, **kwargs)
        elif self.is_json_request:  # added for json response with paging
            return self.json_response(self.request, *args, **kwargs)
        elif self.is_update_request:  # added for row list update
            return self.get_update_view(self.request, *args, **kwargs)
        else:  # standard response with js webix template structure
            return super(WebixListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Prepares the context data for rendering the list view template.

        This method extends the base context with additional data required for
        Webix integration, such as fields, actions, permissions, and pagination settings.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict: The context data for the template.
        """
        context = super(WebixListView, self).get_context_data(**kwargs)
        self.object = None  # bypass for mixin permissions functions
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        context.update(
            {
                "fields": self.get_fields(),
                "orders": self.get_ordering(),
                "actions": self.get_actions(),
                "actions_menu_grouped": self.get_actions_menu_grouped(),
                "enable_json_choices_loading": self.enable_json_choices_loading,
                "choices_filters": self.get_choices_filters(empty=self.enable_json_choices_loading),
                "footer": self.get_footer() if not self.enable_json_loading else None,  # footer only if not paging
                "is_enable_footer": self.is_enable_footer(),
                "get_pk_field": self.get_pk_field(),
                "objects_datatable": self.get_objects_datatable(),
                "is_editable": self.is_editable(),
                "fields_editable": self.get_fields_editable(),
                "column_id": self.get_column_id(self.request),
                "is_enable_column_webgis": self.is_enable_column_webgis(self.request),
                "is_enable_column_copy": self.is_enable_column_copy(self.request),
                "is_enable_column_delete": self.is_enable_column_delete(self.request),
                "is_enable_row_click": self.is_enable_row_click(self.request),
                "type_row_click": self.get_type_row_click(self.request),
                "is_enable_actions": self.is_enable_actions(self.request),
                "title": self.get_title(),
                "header_rows": self.get_header_rows(self.request),
                "adjust_row_height": self.get_adjust_row_height(self.request),
                "is_errors_on_popup": self.is_errors_on_popup(self.request),
                # paging
                "is_json_loading": self.enable_json_loading,
                "paginate_count_default": self.paginate_count_default,
                "paginate_count_key": self.paginate_count_key,
                "paginate_start_key": self.paginate_start_key,
                # extra filters
                "is_installed_django_webix_filter": self.is_installed_django_webix_filter(),
                "is_enabled_django_webix_filter": self.is_enabled_django_webix_filter(),
                # extra layers
                "layers_actions": self.get_layers(area="actions_list"),
                "layers_columns": self.get_layers(area="columns_list"),
            }
        )
        return context


class WebixTemplateListView(WebixListView):
    model = None
    enable_column_copy = False
    enable_column_delete = False
    add_permission = False
    change_permission = False
    delete_permission = False
    view_permission = True
    remove_disabled_buttons = True
    enable_row_click = False

    def get_objects_datatable(self):
        raise ImproperlyConfigured(_("Generic TemplateListView needs to define data for datatable"))

    def get_view_prefix(self):
        return ""
