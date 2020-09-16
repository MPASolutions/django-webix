from django.apps import apps
from django.conf import settings
from django.db.models import AutoField, FieldDoesNotExist
from django.urls import path
from django.utils.text import capfirst

from django_webix.views.generic.base import WebixPermissionsMixin  # utils for permission


class ModelWebixAdmin(WebixPermissionsMixin):
    # WEBIX VIEWS (for fully override)
    create_view = None
    update_view = None
    delete_view = None
    list_view = None

    # JS TEMPLATES
    add_form_template = None
    change_form_template = None
    change_list_template = None
    delete_template = None

    # CREATE AND UPDATE SETTINGS
    enable_button_save_continue = True
    enable_button_save_addanother = True
    enable_button_save_gotolist = True

    # DJANGO WEBIX FORM: OPTION 1
    autocomplete_fields = []
    readonly_fields = []
    fields = None
    exclude = None
    # DJANGO WEBIX FORM: OPTION 2
    form = None

    inlines = []

    # LIST SETTINGS
    ordering = None
    actions = []
    list_display = []
    extra_header = {}

    enable_json_loading = False
    pk_field = None
    title = None
    actions_style = None
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'
    enable_actions = True
    remove_disabled_buttons = False

    # permission custom
    only_superuser = False

    def get_url_pattern_list(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return '%s.%s.list' % info

    def get_url_pattern_create(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return '%s.%s.create' % info

    def get_url_pattern_update(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return '%s.%s.update' % info

    def get_url_pattern_delete(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return '%s.%s.delete' % info

    def get_model_perms(self, request):
        """
        Return a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, ``delete``, and ``view`` mapping to the True/False
        for each of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request),
        }

    def has_module_permission(self, request):
        if self.only_superuser:
            if request.user.is_superuser:
                return True
            return False
        return super().has_module_permission(request)

    def get_field_traverse(self, path):
        _next = self.model
        for j, key in enumerate(path.split('__')):
            if j == 0:
                try:
                    _next = _next._meta.get_field(key)
                except FieldDoesNotExist:
                    # non lo ho trovato allora lo lascio alla view list di arrangiarsi
                    return key
            elif hasattr(_next, 'related_model'):
                _next = _next.related_model._meta.get_field(key)
            else:
                raise Exception('TODO?')
        return _next

    def create_list_display(self, request=None):
        _fields = []
        for j, field_name in enumerate(self.list_display):
            model_field = self.get_field_traverse(field_name)
            if type(model_field) == str:
                header_title = model_field
            else:
                header_title = capfirst(model_field.verbose_name)
            extra_header = ''
            width_adapt = 'fillspace:true' if j == 0 else 'adjust:"all"'
            filter_option = 'serverFilter' if self.enable_json_loading else 'textFilter'
            sort_option = 'server' if self.enable_json_loading else 'string'
            filter_type = 'icontains'
            click_action = None
            if field_name in self.extra_header:
                conf_header = self.extra_header.get(field_name, {})
                if 'header_title' in conf_header:
                    header_title = conf_header.get('header_title', '')
                if 'extra' in conf_header:
                    extra_header = conf_header.get('extra', '')
                if 'width_adapt' in conf_header:
                    width_adapt = conf_header.get('width_adapt', '')
                if 'filter_option' in conf_header:
                    filter_option = conf_header.get('filter_option', '')
                if 'filter_type' in conf_header:
                    filter_type = conf_header.get('filter_type', '')
                if 'click_action' in conf_header:
                    click_action = conf_header.get('click_action', '')
            field_list = {
                'field_name': field_name,
                'datalist_column': '''{{id: "{field_name}",
                header: ["{header_title}", {{content: "{filter}"}}],
                {width_adapt},
                sort: "{sort_option}",
                serverFilterType: "{filter_type}",
                {extra_header} }}'''.format(
                    field_name=field_name,
                    header_title=header_title,
                    filter=filter_option,
                    width_adapt=width_adapt,
                    sort_option=sort_option,
                    filter_type=filter_type,
                    extra_header=extra_header
                )
            }
            if click_action is not None:
                field_list['click_action'] = click_action
            _fields.append(field_list)
        return _fields

    def get_list_display(self, request=None):
        if type(self.list_display[0]) == str:
            return self.create_list_display(request=request)
        else:
            return self.list_display

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__()

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    def get_queryset(self, request):
        return self.model._default_manager.all()

    def get_form_fields(self):
        _fields = []
        for _field in (self.model._meta.fields + self.model._meta.many_to_many):
            if type(_field) != AutoField and \
                (self.exclude is None or _field.name not in self.exclude) and \
                _field.editable is True:
                if self.fields is not None and len(self.fields) > 0:
                    if _field.name in self.fields:
                        _fields.append(_field.name)
                else:
                    _fields.append(_field.name)
        return _fields

    def get_form_create_update(self):
        _admin = self
        if self.form:
            return self.form
        else:
            from django_webix.forms import WebixModelForm

            class WebixAdminCreateUpdateForm(WebixModelForm):
                readonly_fields = _admin.readonly_fields
                autocomplete_fields = _admin.autocomplete_fields

                class Meta:
                    localized_fields = ('__all__')
                    model = _admin.model
                    fields = _admin.get_form_fields()

            return WebixAdminCreateUpdateForm

    def get_layers(self):
        layers = []
        if apps.is_installed("django_webix_leaflet") and getattr(self, 'model', None) is not None:
            for layer in settings.DJANGO_WEBIX_LEAFLET['layers']:
                if layer['modelname'] == f'{self.model._meta.app_label}.{self.model._meta.model_name}':
                    layers.append(layer)
        return layers

    def get_add_view(self):
        _admin = self
        if self.create_view is not None:
            return self.create_view
        else:
            from django_webix.views import WebixCreateView

            class WebixAdminCreateView(WebixCreateView):
                url_pattern_list = 'admin_webix:' + _admin.get_url_pattern_list()
                url_pattern_create = 'admin_webix:' + _admin.get_url_pattern_create()
                url_pattern_update = 'admin_webix:' + _admin.get_url_pattern_update()
                url_pattern_delete = 'admin_webix:' + _admin.get_url_pattern_delete()

                model = _admin.model
                form_class = _admin.get_form_create_update()
                inlines = _admin.inlines
                model_copy_fields = _admin.get_form_fields()
                enable_button_save_continue = _admin.enable_button_save_continue
                enable_button_save_addanother = _admin.enable_button_save_addanother
                enable_button_save_gotolist = _admin.enable_button_save_gotolist

                has_add_permission = _admin.has_add_permission
                has_change_permission = _admin.has_change_permission
                has_delete_permission = _admin.has_delete_permission
                has_view_permission = _admin.has_view_permission

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                get_info_no_add_permission = _admin.get_info_no_add_permission
                get_info_no_change_permission = _admin.get_info_no_change_permission
                get_info_no_delete_permission = _admin.get_info_no_delete_permission
                get_info_no_view_permission = _admin.get_info_no_view_permission

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.add_form_template is not None:
                    template_name = _admin.add_form_template

                def get_queryset(self):
                    return _admin.get_queryset(request=self.request)

            return WebixAdminCreateView

    def get_change_view(self):
        _admin = self
        if self.update_view is not None:
            return self.update_view
        else:
            from django_webix.views import WebixUpdateView

            class WebixAdminUpdateView(WebixUpdateView):
                url_pattern_list = 'admin_webix:' + _admin.get_url_pattern_list()
                url_pattern_create = 'admin_webix:' + _admin.get_url_pattern_create()
                url_pattern_update = 'admin_webix:' + _admin.get_url_pattern_update()
                url_pattern_delete = 'admin_webix:' + _admin.get_url_pattern_delete()

                model = _admin.model
                form_class = _admin.get_form_create_update()
                inlines = _admin.inlines
                model_copy_fields = _admin.get_form_fields()
                enable_button_save_continue = _admin.enable_button_save_continue
                enable_button_save_addanother = _admin.enable_button_save_addanother
                enable_button_save_gotolist = _admin.enable_button_save_gotolist

                has_add_permission = _admin.has_add_permission
                has_change_permission = _admin.has_change_permission
                has_delete_permission = _admin.has_delete_permission
                has_view_permission = _admin.has_view_permission

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                get_info_no_add_permission = _admin.get_info_no_add_permission
                get_info_no_change_permission = _admin.get_info_no_change_permission
                get_info_no_delete_permission = _admin.get_info_no_delete_permission
                get_info_no_view_permission = _admin.get_info_no_view_permission

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.change_form_template is not None:
                    template_name = _admin.change_form_template

                def get_queryset(self):
                    return _admin.get_queryset(request=self.request)

            return WebixAdminUpdateView

    def get_delete_view(self):
        _admin = self
        if self.delete_view is not None:
            return self.delete_view
        else:
            from django_webix.views import WebixDeleteView

            class WebixAdminDeleteView(WebixDeleteView):
                url_pattern_list = 'admin_webix:' + _admin.get_url_pattern_list()
                url_pattern_create = 'admin_webix:' + _admin.get_url_pattern_create()
                url_pattern_update = 'admin_webix:' + _admin.get_url_pattern_update()
                url_pattern_delete = 'admin_webix:' + _admin.get_url_pattern_delete()

                has_add_permission = _admin.has_add_permission
                has_change_permission = _admin.has_change_permission
                has_delete_permission = _admin.has_delete_permission
                has_view_permission = _admin.has_view_permission

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                get_info_no_add_permission = _admin.get_info_no_add_permission
                get_info_no_change_permission = _admin.get_info_no_change_permission
                get_info_no_delete_permission = _admin.get_info_no_delete_permission
                get_info_no_view_permission = _admin.get_info_no_view_permission

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                model = _admin.model

                if _admin.delete_template is not None:
                    template_name = _admin.delete_template

                def get_queryset(self):
                    return _admin.get_queryset(request=self.request)

            return WebixAdminDeleteView

    def get_list_view(self):
        _admin = self
        if self.list_view is not None:
            return self.list_view
        else:
            from django_webix.views import WebixListView

            class WebixAdminListView(WebixListView):
                url_pattern_list = 'admin_webix:' + _admin.get_url_pattern_list()
                url_pattern_create = 'admin_webix:' + _admin.get_url_pattern_create()
                url_pattern_update = 'admin_webix:' + _admin.get_url_pattern_update()
                url_pattern_delete = 'admin_webix:' + _admin.get_url_pattern_delete()

                model = _admin.model
                pk_field = _admin.pk_field
                order_by = _admin.ordering
                actions = _admin.actions
                enable_json_loading = _admin.enable_json_loading
                title = _admin.title
                actions_style = _admin.actions_style
                enable_column_copy = _admin.enable_column_copy
                enable_column_delete = _admin.enable_column_delete
                enable_row_click = _admin.enable_row_click
                type_row_click = _admin.type_row_click
                enable_actions = _admin.enable_actions

                has_add_permission = _admin.has_add_permission
                has_change_permission = _admin.has_change_permission
                has_delete_permission = _admin.has_delete_permission
                has_view_permission = _admin.has_view_permission

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                get_info_no_add_permission = _admin.get_info_no_add_permission
                get_info_no_change_permission = _admin.get_info_no_change_permission
                get_info_no_delete_permission = _admin.get_info_no_delete_permission
                get_info_no_view_permission = _admin.get_info_no_view_permission

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.change_list_template is not None:
                    template_name = _admin.change_list_template

                def get_initial_queryset(self):
                    return _admin.get_queryset(request=self.request)

                # full mode
                @property
                def fields(self):
                    if len(_admin.list_display) > 0:
                        return _admin.get_list_display(request=self.request)
                    else:
                        return None

            return WebixAdminListView

    def get_urls(self):

        # def wrap(view):
        #    def wrapper(*args, **kwargs):
        #        return self.admin_site.admin_view(view)(*args, **kwargs)

        #    wrapper.model_admin = self
        #    return update_wrapper(wrapper, view)

        return [
            path('', self.get_list_view().as_view(), name=self.get_url_pattern_list()),
            path('create/', self.get_add_view().as_view(), name=self.get_url_pattern_create()),
            path('<int:pk>/delete/', self.get_delete_view().as_view(), name=self.get_url_pattern_delete()),
            path('<int:pk>/update/', self.get_change_view().as_view(), name=self.get_url_pattern_update()),
            #            path('', wrap(self.get_list_view), name='%s_%s_changelist' % info),
            #            path('add/', wrap(self.get_add_view), name='%s_%s_add' % info),
            #            path('<path:object_id>/delete/', wrap(self.get_delete_view), name='%s_%s_delete' % info),
            #            path('<path:object_id>/change/', wrap(self.get_change_view), name='%s_%s_change' % info),
        ]

    @property
    def urls(self):
        return self.get_urls()
