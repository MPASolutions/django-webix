from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.db.models import Case, When, Value, CharField, Func, F
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.utils.encoding import force_str

from django_webix.views import (
    WebixListView as ListView,
    WebixDeleteView as DeleteView,
    WebixCreateView as CreateView,
    WebixUpdateView as UpdateView,
    WebixTemplateView as TemplateView
)
from django_webix.contrib.filter.forms import WebixFilterForm
from django_webix.contrib.filter.models import WebixFilter
from django_webix.contrib.filter.utils.json_converter import get_JSON_for_JQB, get_JSON_for_DB, get_JSON_from_DB
from django_webix.contrib.filter.utils.check import model_is_enabled, check_filter, check_config
from django_webix.contrib.filter.utils.config import _get_config_new, get_limit_suggest

from django.utils.html import escapejs
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy


class DjangoWebixFilterView(TemplateView):
    template_name = "django_webix/filter/filters.js"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FilterConfigView(View):
    def get(self, *args, **kwargs):
        app_label = kwargs.get('app_label')
        model_name = kwargs.get('model_name')
        model_class = apps.get_model(app_label=app_label, model_name=model_name)
        if not model_is_enabled(model_class):
            return JsonResponse({}, safe=False)

        return JsonResponse(_get_config_new(model_class))

    def _get_model_config(self, model_class, already_visited, prefix=None, model_prefix=None):
        # Create model configuration dict without fields
        _model_config = {
            "model": "{app_label}.{model_name}".format(
                app_label=model_class._meta.app_label,
                model_name=model_class._meta.model_name
            ),
            "label": model_class._meta.verbose_name,
            "fields": []
        }

        # Iterate through model fields excluding relations and adds it to model configuration dict
        for field in model_class._meta.fields:
            field_name = field.name
            if prefix is not None:
                field_name = "{prefix}__{field_name}".format(prefix=prefix, field_name=field.name)
            field_label = field.verbose_name
            if model_prefix is not None:
                field_label = "{} / {}".format(field_label, model_prefix)
            # _choices = getattr(field, 'choices', None)
            _model_config['fields'].append({
                "id": field_name,
                "label": field_label,
                "type": field.get_internal_type(),
                "operators": list(field.get_lookups().keys()),
                # **self.matches.get(type(field), {})
            })

        # Generate results list with model configuration dict
        results = [_model_config]

        # Iterate trough model relations and adds recursively its fields
        relation_fields = list(filter(
            lambda field: issubclass(type(field), models.ForeignKey) or
                          issubclass(type(field), ForeignObjectRel) or
                          issubclass(type(field), models.ManyToManyField) or
                          issubclass(type(field), GenericRelation),
            # TODO: add `ManyToOneRel`?
            model_class._meta.get_fields()
        ))
        for field in relation_fields:
            if issubclass(type(field), models.ForeignKey):
                model = field.remote_field.get_related_field().model
                model_name = "{app_label}.{model_name}".format(
                    app_label=model._meta.app_label,
                    model_name=model._meta.model_name
                )
                if model_name in already_visited:
                    continue
                results.append(self._get_model_config(
                    model,
                    already_visited=already_visited + [_model_config["model"]],
                    prefix=field.name,
                    model_prefix=model._meta.verbose_name
                ))
            elif issubclass(type(field), ForeignObjectRel):
                model = field.related_model
                model_name = "{app_label}.{model_name}".format(
                    app_label=model._meta.app_label,
                    model_name=model._meta.model_name
                )
                if model_name in already_visited:
                    continue
                results.append(self._get_model_config(
                    model,
                    already_visited=already_visited + [_model_config["model"]],
                    prefix=field.remote_field.related_query_name(),
                    model_prefix=model._meta.verbose_name
                ))
            elif issubclass(type(field), models.ManyToManyField):
                model = field.remote_field.get_related_field().model
                model_name = "{app_label}.{model_name}".format(
                    app_label=model._meta.app_label,
                    model_name=model._meta.model_name,
                    model_prefix=model._meta.verbose_name
                )
                if model_name in already_visited:
                    continue
                results.append(self._get_model_config(
                    model,
                    already_visited=already_visited + [_model_config["model"]],
                    prefix=field.name
                ))
            elif issubclass(type(field), GenericRelation):
                model = field.related_model
                model_name = "{app_label}.{model_name}".format(
                    app_label=model._meta.app_label,
                    model_name=model._meta.model_name
                )
                if model_name in already_visited:
                    continue
                results.append(self._get_model_config(
                    model,
                    already_visited=already_visited + [_model_config["model"]],
                    prefix=field.name
                ))

        # Returns model configuration dict only if the current model class is not the starting model
        # otherwise returns final dict
        if prefix is None:
            operators = list(set([
                operator for model in results for field in model["fields"] for operator in field["operators"]
            ]))
            return {
                "models": results,
                "operators": operators  # [{"type": lookup, **self.matches.get(lookup, {})} for lookup in lookups]
            }
        return _model_config


class FilterSuggestExact(View):
    def get(self, *args, **kwargs):
        filed_complete = kwargs.get('field')
        names = filed_complete.split('.')
        limit = self.request.GET.get('limit', None)
        filter_value = self.request.GET.get('filter[value]', None)
        display_field = self.request.GET.get('display_field', None)

        if len(names) == 3:
            try:
                model_class = apps.get_model(app_label=names[0], model_name=names[1])
                qs = model_class.objects.all()
                field_name = names[2]

                if isinstance(model_class._meta.get_field(field_name), ArrayField):
                    qs = qs.annotate(
                        dw_filter_unpacked_field=Func(F(field_name), function='unnest')
                    )
                    field_name = 'dw_filter_unpacked_field'
                    suggest = [{field_name: str(x[field_name])} for x in qs.values(field_name).distinct()]

                    if filter_value is not None and filter_value != '':
                        suggest = list(filter(lambda x: filter_value in x[field_name], suggest))

                    if limit is not None and limit.isnumeric():
                        limit = int(limit)
                        suggest = list(suggest[:limit])

                else:
                    if filter_value is not None and filter_value != '':
                        qs = qs.filter(**{field_name + '__icontains': filter_value})

                    if display_field is not None and display_field != '':
                        qs = qs.values(field_name, display_field)
                    else:
                        qs = qs.values(field_name)

                    qs = qs.distinct()
                    if limit is not None and limit.isnumeric():
                        limit = int(limit)
                        suggest = list(qs[:limit])
                    else:
                        suggest = list(qs)

                if display_field is not None and display_field != '':
                    suggest = [{'id': x[field_name], 'value': x[display_field]} for x in suggest]
                else:
                    suggest = [{'id': x[field_name], 'value': x[field_name]} for x in suggest]

                return JsonResponse(suggest, safe=False)
            except:
                pass
        return JsonResponse({}, safe=False)


class WebixFilterMixin:
    def get_container_id(self, request):
        if self.is_popup():
            return 'content_query_builder'
        return settings.WEBIX_CONTAINER_ID

    def is_installed_django_webix_filter(self):
        return False

    def has_view_permission(self, request, obj=None):
        permission = super().has_view_permission(request, obj)
        if obj is not None and obj.visibility == 'public':
            return permission and True
        elif obj is not None and obj.visibility == 'private':
            return permission and (
                obj.insert_user == request.user or
                obj.insert_user is None or
                (
                    obj.shared_edit_group is True and
                    obj.insert_user.groups.filter(pk__in=request.user.groups.values('pk')).exists()
                )
            )
        elif obj is not None and obj.visibility == 'restricted':
            return permission and (
                obj.insert_user == request.user or
                obj.insert_user is None or
                obj.assignees_groups.filter(user=request.user).exists() or
                (
                    obj.shared_edit_group is True and
                    obj.insert_user.groups.filter(pk__in=request.user.groups.values('pk')).exists()
                )
            )
        return permission

    def has_change_permission(self, request, obj=None):
        permission = super().has_change_permission(request, obj)
        if obj is not None:
            return permission and (
                obj.insert_user == request.user or
                obj.insert_user is None or
                obj.assignees_groups.filter(user=request.user).exists() or
                (
                    obj.shared_edit_group is True and
                    obj.insert_user.groups.filter(pk__in=request.user.groups.values('pk')).exists()
                )
            )
        return permission

    def has_delete_permission(self, request, obj=None):
        permission = super().has_delete_permission(request, obj)
        if obj is not None:
            return permission and (
                obj.insert_user == request.user or
                obj.insert_user is None
            )
        return permission


class WebixFilterList(WebixFilterMixin, ListView):
    model = WebixFilter
    is_enable_column_geo = False
    enable_row_click = True
    enable_column_copy = False
    type_row_click = 'single'
    actions_style = 'buttons'

    template_name = 'django_webix/filter/list.js'

    def get_actions(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config_check'] = check_config()[0]
        if self.kwargs.get('app_label') and self.kwargs.get('model_name'):
            context['list_view_prefix'] = '{}_{}_'.format(
                self.kwargs.get('app_label'),
                self.kwargs.get('model_name')
            )
        return context

    def get_initial_queryset(self):
        qs = super().get_initial_queryset()

        qs = qs.annotate(
            visibility_display=Case(
                *[When(visibility=k, then=Value(force_str(v))) for k, v in self.model._meta.get_field('visibility').choices],
                default=Value(''),
                output_field=CharField()
            )
        )
        return qs

    def get_queryset(self, initial_queryset=None):
        qs = super().get_queryset(initial_queryset=initial_queryset)

        app_label = self.kwargs.get('app_label')
        model_name = self.kwargs.get('model_name')
        if app_label is not None and model_name is not None:
            qs = qs.filter(model=f'{app_label}.{model_name}')

        return qs

    def get_url_create(self):
        _url_create = super().get_url_create()

        app_label = self.kwargs.get('app_label', None)
        model_name = self.kwargs.get('model_name', None)

        if _url_create is not None and app_label is not None and model_name is not None:
            if '?' in _url_create:
                _url_create += f'&model={app_label}.{model_name}&SEND_INITIAL_DATA=true'
            else:
                _url_create += f'?model={app_label}.{model_name}&SEND_INITIAL_DATA=true'

        return _url_create

    def get_fields(self, fields=None):
        _fields = [
            {
                'field_name': 'title',
                'datalist_column': format_lazy(
                    '''{{
                    id: "title",
                    header: ["{}", {{content: "textFilter"}}],
                    adjust: "all",
                    fillspace: true
                    }} ''',
                    escapejs(_("Title")))
            },
            {
                'field_name': 'description',
                'datalist_column': format_lazy(
                    '''{{
                    id: "description",
                    header: ["{}", {{content: "textFilter"}}],
                    adjust: "all",
                    fillspace: true
                    }} ''',
                    escapejs(_("Description")))
            },
            {
                'field_name': 'model',
                'datalist_column': format_lazy(
                    '''{{
                    id: "model",
                    header: ["{}", {{content: "textFilter"}}],
                    adjust: "all",
                    fillspace: true
                    }} ''',
                    escapejs(_("Model")))
            },
            {
                'field_name': 'visibility_display',
                'datalist_column': format_lazy(
                    '''{{
                    id: "visibility_display",
                    header: ["{}", {{content: "textFilter"}}],
                    adjust: "all",
                    fillspace: true
                    }} ''',
                    escapejs(_("Visibility")))
            }
        ]
        return super().get_fields(fields = _fields)


class WebixFilterCreate(WebixFilterMixin, CreateView):
    model = WebixFilter
    form_class = WebixFilterForm
    template_name = 'django_webix/filter/create_update.js'

    enable_button_save_addanother = False
    enable_button_save_continue = False

    def get_url_list(self):
        if self.is_popup():
            if self.request.GET.get('model', None):
                app_label, module_name = self.request.GET.get('model', None).split('.')
                return self.wrap_url_popup(reverse('dwfilter.webixfilter.list_model', kwargs={
                    'app_label': app_label,
                    'model_name': module_name
                }))
            if self.object is not None:
                app_label, module_name = self.object.model.split('.')
                return self.wrap_url_popup(reverse('dwfilter.webixfilter.list_model', kwargs={
                    'app_label': app_label,
                    'model_name': module_name
                }))
        return super().get_url_list()

    def forms_valid(self, form, inlines, **kwargs):
        _filter = form.instance.filter
        form.instance.filter = get_JSON_for_DB(_filter)
        if self.request.user.is_authenticated:
            form.instance.insert_user = self.request.user
        return super().forms_valid(form, inlines, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if "visibility" in settings.DJANGO_WEBIX_FILTER:
            # Check configuration of the first group found
            group = self.request.user.groups.filter(
                name__in=settings.DJANGO_WEBIX_FILTER["visibility"].keys()
            ).first()
            # Set default visibility value
            if group is not None and "default" in settings.DJANGO_WEBIX_FILTER["visibility"][group.name]:
                initial["visibility"] = settings.DJANGO_WEBIX_FILTER["visibility"][group.name]["default"].value
        if "shared_edit_groups" in settings.DJANGO_WEBIX_FILTER:
            # Check configuration of the first group found
            group = self.request.user.groups.filter(
                name__in=settings.DJANGO_WEBIX_FILTER["shared_edit_groups"].keys()
            ).first()
            # Set default shared_edit_groups value
            if group is not None and "default" in settings.DJANGO_WEBIX_FILTER["shared_edit_groups"][group.name]:
                initial["shared_edit_group"] = \
                    settings.DJANGO_WEBIX_FILTER["shared_edit_groups"][group.name]["default"]
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "visibility" in settings.DJANGO_WEBIX_FILTER:
            # Check configuration of the first group found
            group = self.request.user.groups.filter(
                name__in=settings.DJANGO_WEBIX_FILTER["visibility"].keys()
            ).first()
            # Set visibility options
            if group is not None and \
                "choices" in settings.DJANGO_WEBIX_FILTER["visibility"][group.name] and \
                isinstance(settings.DJANGO_WEBIX_FILTER["visibility"][group.name]["choices"], list):
                kwargs["visibility_choices"] = \
                    [i.value for i in settings.DJANGO_WEBIX_FILTER["visibility"]["Admin"]["choices"]]
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'limit_suggest': get_limit_suggest()
        })
        return context


class WebixFilterUpdate(WebixFilterMixin, UpdateView):
    model = WebixFilter
    form_class = WebixFilterForm
    template_name = 'django_webix/filter/create_update.js'

    enable_button_save_addanother = False
    enable_button_save_continue = False

    def get_url_list(self):
        if self.is_popup() and self.object is not None:
            app_label, module_name = self.object.model.split('.')
            return self.wrap_url_popup(reverse('dwfilter.webixfilter.list_model', kwargs={
                'app_label': app_label,
                'model_name': module_name
            }))
        else:
            return super().get_url_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        correct = True
        if obj is not None:
            json_elaborated = get_JSON_from_DB(obj.filter)
            initial_model = obj.model
            if json_elaborated is not None and initial_model is not None:
                names = initial_model.split('.')
                try:
                    model_class = apps.get_model(app_label=names[0], model_name=names[1])
                    json_elaborated = get_JSON_for_JQB(json_elaborated, model_class)
                    if not check_filter(json_elaborated):
                        correct = False
                except:
                    correct = False

        context.update({
            'check_filter': correct,
            'limit_suggest': get_limit_suggest()
        })
        return context

    def forms_valid(self, form, inlines, **kwargs):
        form.instance.filter = get_JSON_for_DB(form.instance.filter)
        return super().forms_valid(form, inlines, **kwargs)


class WebixFilterDelete(WebixFilterMixin, DeleteView):
    model = WebixFilter

    def get_url_list(self):
        if self.is_popup() and self.object is not None:
            app_label, module_name = self.object.model.split('.')
            return self.wrap_url_popup(reverse('dwfilter.webixfilter.list_model', kwargs={
                'app_label': app_label,
                'model_name': module_name
            }))
        else:
            return super().get_url_list()

    def get_failure_delete_related_objects(self, request, obj=None):
        INSTANCES = []
        return INSTANCES
