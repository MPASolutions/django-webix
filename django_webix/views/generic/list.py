
from copy import deepcopy
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models import F, ManyToManyField, Case, When, Value, BooleanField
from django.db.models.functions import Coalesce
from django.http import JsonResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.views.generic import ListView
from django.db.models.query import QuerySet

from django_webix.forms import WebixModelForm
from django_webix.views import WebixUpdateView
from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin
from django_webix.utils.layers import get_model_geo_field_names

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    GEOSGeometry = object

try:
    from django.contrib.gis.geos import MultiPolygon
except ImportError:
    MultiPolygon = object


def get_action_dict(request, action):
    # needed for set var with NOne as value
    form = action.form(request=request) if hasattr(action, 'form') and action.form is not None else None
    template_view = action.template_view if hasattr(action, 'template_view') and action.template_view is not None else None
    form_view = action.form_view if hasattr(action, 'form_view') and action.form_view is not None else None

    return {
        'func': action,
        'action_key': action.action_key,
        'response_type': action.response_type,
        'allowed_permissions': action.allowed_permissions,
        'short_description': action.short_description,
        'modal_header': action.modal_header,
        'modal_title': action.modal_title,
        'modal_click': action.modal_click,
        'modal_ok': action.modal_ok,
        'modal_cancel': action.modal_cancel,
        'form': form,
        'reload_list': getattr(action, 'reload_list', True),
        'template_view': template_view,
        'dynamic': action.dynamic,
        'form_view_template': action.form_view_template,
        'form_view': form_view
    }


def get_actions_flexport(request, model):
    _actions = []
    # add flexport actions
    if apps.is_installed('flexport') and model is not None:
        from django.contrib.contenttypes.models import ContentType
        from flexport.views import create_extraction
        from flexport.models import Export

        model_ct = ContentType.objects.get(model=model._meta.model_name,
                                           app_label=model._meta.app_label)
        flexport_actions = {}

        def action_builder(export_instance):
            _action = lambda listview, request, qs: create_extraction(request, export_instance.id, qs)
            _action.__name__ = 'flexport_action_%s' % export_instance.id  # verificare se è corretto
            _action.response_type = 'blank'
            _action.short_description = export_instance.action_name
            _action.action_key = 'flexport_{}'.format(export_instance.id)
            _action.allowed_permissions = []
            _action.modal_header = _('Fill in the form')
            _action.modal_title = _("Are you sure you want to proceed with this action?")
            _action.modal_click = _("Go")
            _action.modal_ok = _("Proceed")
            _action.modal_cancel = _("Undo")
            _action.reload_list = False
            _action.dynamic = False
            _action.form_view_template = None
            _action.form_view = None
            return _action

        for export_instance in Export.objects.filter(model=model_ct, active=True):
            if export_instance.is_enabled(request):
                _actions.append(action_builder(export_instance))
    return _actions


class WebixListView(WebixBaseMixin,
                    WebixPermissionsMixin,
                    WebixUrlMixin,
                    ListView):
    # request vars
    http_method_names = ['get', 'post']  # enable POST for filter porpouse

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
    paginate_count_default = 100
    paginate_start_default = 0
    paginate_count_key = 'count'
    paginate_start_key = 'start'

    # template vars
    template_name = 'django_webix/generic/list.js'
    title = None
    actions_style = None
    enable_column_webgis = True
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'  # or 'double'
    enable_actions = True

    fields_editable = []

    def is_errors_on_popup(self, request):
        return self.errors_on_popup

    def is_installed_django_webix_filter(self):
        return apps.is_installed('django_webix.contrib.filter')

    def is_enabled_django_webix_filter(self):
        if self.is_installed_django_webix_filter() and self.model is not None:
            from django_webix.contrib.filter.utils.config import model_is_enabled
            return model_is_enabled(self.model)
        return False

    def get_header_rows(self, request):
        return self.header_rows

    def _optimize_select_related(self, qs):
        # extrapolate the information to populate `select_related`
        _select_related = []
        if self.get_fields() is not None:
            for field in self.get_fields():
                if field.get('field_name') is not None:
                    field_name = field.get('field_name')
                    _model = self.model
                    _field = None
                    _related = []
                    for name in field_name.split('__'):
                        try:
                            _field = _model._meta.get_field(name)
                            if isinstance(_field, ManyToManyField):  # Check if field is M2M
                                raise FieldDoesNotExist()
                        except FieldDoesNotExist:
                            break  # name is probably a lookup or transform such as __contains
                        if hasattr(_field, 'related_model') and _field.related_model is not None:
                            _related.append(name)
                            _model = _field.related_model  # field is a relation
                        else:
                            break  # field is not a relation, any name that follows is probably a lookup or transform
                    _related = '__'.join(_related)
                    if _related != '':
                        _select_related.append(_related)
            qs = qs.select_related(*_select_related)
        return qs

    def _model_translations(self, qs):
        if apps.is_installed('modeltranslation'):
            from modeltranslation.fields import TranslationFieldDescriptor
            fields = [field for field in self.get_fields() or [] if field.get('field_name') is not None]
            for field in fields:
                field_name = field.get('field_name')
                _model = self.model
                _field = None
                for name in field_name.split('__'):
                    try:
                        _field = _model._meta.get_field(name)
                        if isinstance(_field, ManyToManyField):  # Check if field is M2M
                            raise FieldDoesNotExist()
                    except FieldDoesNotExist:
                        break  # name is probably a lookup or transform such as __contains
                    if hasattr(_field, 'related_model') and _field.related_model is not None:
                        _model = _field.related_model  # field is a relation
                    else:
                        break  # field is not a relation, any name that follows is probably a lookup or transform

                # Check if last field of last model is translated (exclude initial model)
                if _field is not None and _model != self.model:
                    _field_attribute = getattr(_model, _field.name, None)
                    if isinstance(_field_attribute, TranslationFieldDescriptor):
                        qs = qs.annotate(**{field_name: Coalesce('{}_{}'.format(field_name, get_language()), field_name)})
        return qs

    def get_column_id(self, request):
        return self.column_id or 'id'

    def get_adjust_row_height(self, request):
        return self.adjust_row_height

    def get_fields(self, fields=None):
        if self.fields is not None:
            _in_fields = deepcopy(self.fields)
            # otherwise in the loop below the static fields attribute is redefined and they don't work lazy_translations
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
                datalist_column = _field['datalist_column']
                if type(datalist_column) == dict:
                    if 'template_string' in datalist_column:
                        template = Template(datalist_column['template'])
                    elif 'template_name' in datalist_column:
                        template = get_template(datalist_column['template_name'])
                    else:
                        raise Exception('Template is not defined')
                    context = Context(datalist_column.get('context', {}))
                else:  # string
                    template = Template(datalist_column)
                    context = Context({})
                _field['datalist_column'] = template.render(context)
                # check server into datalist_column if is json loading
                if self.enable_json_loading:
                    if 'server' in _field['datalist_column']:
                        server_filter = True
                _fields.append(_field)
            if server_filter == False:
                raise Exception('Must be at least one server filter')
            return _fields

    def get_annotations_geoavailable(self, geo_field_names):
        annotations = {}
        for geo_field_name in geo_field_names:
            annotations.update({
                f'{geo_field_name}_available': Case(When(**{f'{geo_field_name}__isnull': False}, then=True),
                                                    default=Value(False),
                                                    output_field=BooleanField())
            })
        return annotations

    def get_initial_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def get_queryset(self, initial_queryset=None):
        # bypass improperly configured for custom queryset without model
        if self.model:
            if initial_queryset is not None:
                qs = initial_queryset
            else:
                qs = self.get_initial_queryset()

            qs = self._model_translations(qs)  # Check model translations

            if apps.is_installed('django_filtersmerger'):
                from django_filtersmerger import FilterMerger
                filter_merger = FilterMerger(request=self.request)
                qs = filter_merger.get_queryset(self.model, initial_queryset=qs)

            # annotate geo available
            if self.is_enable_column_webgis(self.request):
                geo_field_names = get_model_geo_field_names(self.model)
                annotations = self.get_annotations_geoavailable(geo_field_names)
                qs = qs.annotate(**annotations)

            # optimize select related queryset (only if fields are defined)
            qs = self._optimize_select_related(qs)  # TODO

            return self.apply_ordering(qs)

        return None

    def get_choices_filters(self):
        _fields_choices = {}
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get('datalist_column') is not None:
                    if ('serverSelectFilter' in field.get('datalist_column') or
                       'serverRichSelectFilter' in field.get('datalist_column') or
                       'serverMultiSelectFilter' in field.get('datalist_column') or
                       'serverMultiComboFilter' in field.get('datalist_column')):
                        field_name = field.get('field_name')
                        # TODO: there are no null option
                        _fields_choices[field_name] = [str(i) for i in
                            self.get_queryset().filter(**{field_name + '__isnull': False}).values_list(field_name,
                                                                                                   flat=True).distinct().order_by()]

        return _fields_choices

    def is_enable_footer(self):
        is_footer = False
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get('footer') is not None:
                    is_footer = True
        return is_footer

    def get_footer(self):
        if self.is_enable_footer() and self.model is not None:
            qs = self.get_queryset()
            aggregation_dict = {}
            for field in self.get_fields():
                if field.get('footer') is not None:
                    aggregation_dict.update({field.get('field_name') + '_footer': field.get('footer')})
            qs = qs.aggregate(**aggregation_dict)
            return qs
        else:
            return None

    def get_ordering(self):
        if self.request.POST.getlist('sort[]'):
            return self.request.POST.getlist('sort[]')
        else:
            if self.order_by is not None:
                return self.order_by
            else:
                return (self.get_pk_field(),)

    def apply_ordering(self, queryset):
        order = self.get_ordering()
        return queryset.order_by(*order)

    def get_paginate_count(self):
        paginate_count = self.request.GET.get(self.paginate_count_key,
                                              self.request.POST.get(self.paginate_count_key,
                                                                    self.paginate_count_default))
        try:
            return int(paginate_count)
        except ValueError:
            raise Exception(_('Paginate count is not integer'))

    def get_paginate_start(self):
        paginate_start = self.request.GET.get(self.paginate_start_key,
                                              self.request.POST.get(self.paginate_start_key,
                                                                    self.paginate_start_default))
        try:
            return int(paginate_start)
        except ValueError:
            raise Exception(_('Paginate start is not integer'))

    def paginate_queryset(self, queryset, page_size): # page_size not used
        paginate_count = self.get_paginate_count()
        paginate_start = self.get_paginate_start()
        return queryset[paginate_start: paginate_start + paginate_count]

    def _get_objects_datatable_values(self, qs):
        values = [self.get_pk_field()]
        fields = self.get_fields()
        if fields is not None:
            for field in fields:
                if field.get('field_name') is not None and \
                    (field.get('queryset_exclude') is None or field.get('queryset_exclude') != True):
                    values.append(field['field_name'])
        if self.is_enable_column_webgis(self.request):
            for field_name in get_model_geo_field_names(self.model):
                values += [f'{field_name}_available']
        data = qs.values(*values,
                         **({'id': F('pk')} if self.get_pk_field() != 'id' and not hasattr(self.model, 'id') else {}))
        return data

    def get_objects_datatable(self):
        if self.model and not self.enable_json_loading:
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            #raise Exception(qs)
            # pagination (applied only for json request)
            # if self.is_json_request:
            #    qs = self.paginate_queryset(qs, None)
            # build output
            if qs is not None:
                if type(qs) == list:
                    return qs
                else:  # queryset
                    # apply ordering
                    qs = self.apply_ordering(qs)
                    return self._get_objects_datatable_values(qs)
        return None

    def filters_objects_datatable(self, qs):
        ids = self.request.POST.get('ids', '').split(',')
        ids = list(set(ids) - set([None, '']))

        if len(ids) > 0:
            if type(qs) == list:
                for item in qs:
                    if item.get('id') not in ids:
                        qs.remove(item)
            elif self.model is not None:
                auto_field_name = self.model._meta.get_field(self.get_pk_field()).name
                qs = qs.filter(**{auto_field_name + '__in': ids})
        return qs

    def get_pk_field(self):
        if self.pk_field is not None:
            return self.pk_field
        return 'id'

    ########### TEMPLATE BUILDER ###########

    def _get_action_dict(self, action):
        return get_action_dict(self.request, action)

    def _get_actions_flexport(self):
        return get_actions_flexport(self.request, self.model)

    def get_actions(self):
        '''
        Return list of actions to be executed on listview
        :return:
        '''
        # _actions = self.actions
        # tentativo di fix delle azioni sbagliate
        _actions = deepcopy(self.actions)
        _actions += self._get_actions_flexport()

        _dict_actions = {}
        for _action in _actions:
            _dict_actions[_action.action_key] = self._get_action_dict(_action)

        return _dict_actions

    def get_actions_style(self):
        _actions_style = None
        if self.actions_style is None:
            _actions_style = 'select'
        elif self.actions_style in ['buttons', 'select']:
            _actions_style = self.actions_style
        else:
            raise ImproperlyConfigured(_(
                "Actions style is improperly configured"
                " only options are 'buttons' or 'select' (select by default)."))
        return _actions_style

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

    ########### RESPONSE BUILDER ###########

    @property
    def is_json_request(self):
        if 'json' in self.request.GET or 'json' in self.request.POST:
            return True
        else:
            return False

    @property
    def is_action_request(self):
        if 'action' in self.request.GET or 'action' in self.request.POST:
            return True
        else:
            return False

    @property
    def is_update_request(self):
        if 'update' in self.request.GET or 'update' in self.request.POST:
            return True
        else:
            return False

    def is_editable(self):
        return len(self.fields_editable) > 0

    def get_update_form_class(self):
        _list_view = self
        class UpdateForm(WebixModelForm):
            class Meta:
                localized_fields = ('__all__')
                model = _list_view.model
                fields = _list_view.get_fields_editable()
        return UpdateForm

    def get_update_view(self, request, *args, **kwargs):
        kwargs.update({'pk':request.GET.get('id',request.POST.get('id'))})

        _list_view = self
        # TODO: is login is required depends if list has login required
        @method_decorator(login_required, name='dispatch')
        class ListUpdateView(WebixUpdateView):
            success_url ='' #for exception bypass
            http_method_names = ['post'] # only update directly without render
            model = _list_view.model
            def get_form_class(self):
                return _list_view.get_update_form_class()
            def response_valid(self, success_url=None, **kwargs):
                return JsonResponse({'status': True})
            def response_invalid(self, success_url=None, **kwargs):
                return JsonResponse({'status': False})
        return ListUpdateView.as_view()(request, *args, **kwargs)

    def get_fields_editable(self):
        return self.fields_editable

    def get_request_action(self):
        action_name = self.request.POST.get('action', self.request.GET.get('action', None))
        return self.get_actions().get(action_name)['func']

    def post(self, request, *args, **kwargs):  # all post works like get
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(WebixListView, self).get(request, *args, **kwargs)

    def json_response(self, request, *args, **kwargs):
        # ONLY for get_queryset() -> qs and not get_queryset() -> list
        _data = []
        total_count = 0
        if self.model:
            qs = self.get_queryset(initial_queryset=self.get_initial_queryset())
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # apply ordering
            qs = self.apply_ordering(qs)
            # total count
            total_count = qs.only(self.get_pk_field()).count()
            # apply pagination
            qs_paginate = self.paginate_queryset(qs, None)
            # build output
            if qs_paginate is not None:
                if type(qs_paginate) == list:
                    raise Exception(
                        _('Json response is available only if get_queryset() return a queryset and not a list'))
                else:  # queryset
                    _data = self._get_objects_datatable_values(qs_paginate)

        pos = self.get_paginate_start()
        # output must be list and not values of queryset
        data = {
            "footer": self.get_footer() if pos == 0 else None,  # footer is computed only for first page
            'is_enable_footer': self.is_enable_footer(),
            "count": self.get_paginate_count(),
            "total_count": total_count,
            "pos": pos,
            "data": list(_data)
        }
        return JsonResponse(data, safe=False)

    def action_response(self, request, *args, **kwargs):
        action_function = self.get_request_action()
        if action_function is None:
            raise Http404(_('This action is not registered'))
        else:
            # check permissions
            for key in getattr(action_function, 'allowed_permissions', []):
                if hasattr(self, 'has_{}_permission'.format(key)):
                    if getattr(self, 'has_{}_permission'.format(key))(request) != True:
                        raise Http404(_('Permission denied: {}'.format(key)))
                else:
                    raise Http404(_('This permission is not registered on this class'))
            # execution
            qs = self.get_queryset()
            # filters application (like IDS selections)
            qs = self.filters_objects_datatable(qs)
            # apply ordering
            if type(qs) != list:
                qs = self.apply_ordering(qs)
            return action_function(self, request, qs)

    def dispatch(self, *args, **kwargs):
        if not self.has_view_permission(request=self.request):
            raise PermissionDenied(_('View permission is not allowed'))
        if self.is_action_request:  # added for action response
            return self.action_response(self.request, *args, **kwargs)
        elif self.is_json_request:  # added for json response with paging
            return self.json_response(self.request, *args, **kwargs)
        elif self.is_update_request:  # added for row list update
            return self.get_update_view(self.request, *args, **kwargs)
        else:  # standard response with js webix template structure
            return super(WebixListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixListView, self).get_context_data(**kwargs)
        self.object = None  # bypass for mixin permissions functions
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        context.update({
            'fields': self.get_fields(),
            'orders': self.get_ordering(),
            'actions': self.get_actions(),
            'choices_filters': self.get_choices_filters(),
            'footer': self.get_footer() if not self.enable_json_loading else None,  # footer only if not paging
            'is_enable_footer': self.is_enable_footer(),
            'get_pk_field': self.get_pk_field(),
            'objects_datatable': self.get_objects_datatable(),
            'is_editable': self.is_editable(),
            'fields_editable': self.get_fields_editable(),
            'column_id': self.get_column_id(self.request),
            'is_enable_column_webgis': self.is_enable_column_webgis(self.request),
            'is_enable_column_copy': self.is_enable_column_copy(self.request),
            'is_enable_column_delete': self.is_enable_column_delete(self.request),
            'is_enable_row_click': self.is_enable_row_click(self.request),
            'type_row_click': self.get_type_row_click(self.request),
            'is_enable_actions': self.is_enable_actions(self.request),
            'actions_style': self.get_actions_style(),
            'title': self.get_title(),
            'header_rows': self.get_header_rows(self.request),
            'adjust_row_height': self.get_adjust_row_height(self.request),
            'is_errors_on_popup': self.is_errors_on_popup(self.request),
            # paging
            'is_json_loading': self.enable_json_loading,
            'paginate_count_default': self.paginate_count_default,
            'paginate_count_key': self.paginate_count_key,
            'paginate_start_key': self.paginate_start_key,
            # extra filters
            'is_installed_django_webix_filter': self.is_installed_django_webix_filter(),
            'is_enabled_django_webix_filter': self.is_enabled_django_webix_filter(),
        })
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
        return ''
