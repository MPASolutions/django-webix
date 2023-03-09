from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import AutoField, ForeignKey
from django.db.models.fields import BooleanField, DateField, DateTimeField
from django.urls import path
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django_webix.utils.decorators import script_login_required
from django.utils.decorators import method_decorator

from django_webix.views.generic.base import WebixPermissionsBaseMixin
from django_webix.utils.layers import get_layers


class ModelWebixAdminPermissionsMixin(WebixPermissionsBaseMixin):

    def has_add_permission(self, view, request):
        if view is not None:
            return super(view.__class__, view).has_add_permission(request)
        else:
            return self._has_add_permission(request)

    def has_change_permission(self, view, request, obj=None):
        if view is not None:
            return super(view.__class__, view).has_change_permission(request, obj)
        else:
            return self._has_change_permission(request, obj)

    def has_delete_permission(self, view, request, obj=None):
        if view is not None:
            return super(view.__class__, view).has_delete_permission(request, obj)
        else:
            return self._has_delete_permission(request, obj)

    def has_view_permission(self, view, request, obj=None):
        if view is not None:
            return super(view.__class__, view).has_view_permission(request, obj)
        else:
            return self._has_view_permission(request, obj)

    def get_info_no_add_permission(self, view, has_permission, request):
        if view is not None:
           return super(view.__class__, view).get_info_no_add_permission(has_permission, request)
        else:
            return self._get_info_no_add_permission(has_permission, request)

    def get_info_no_change_permission(self, view, has_permission, request, obj=None):
        if view is not None:
            return super(view.__class__, view).get_info_no_change_permission(has_permission, request, obj)
        else:
            return self._get_info_no_change_permission(has_permission, request, obj)

    def get_info_no_delete_permission(self, view, has_permission, request, obj=None):
        if view is not None:
            return super(view.__class__, view).get_info_no_delete_permission(has_permission, request, obj)
        else:
            return self._get_info_no_delete_permission(has_permission, request, obj)

    def get_info_no_view_permission(self, view, has_permission, request, obj=None):
        if view is not None:
            return super(view.__class__, view).get_info_no_view_permission(has_permission, request, obj)
        else:
            return self._get_info_no_view_permission(has_permission, request, obj)


class ModelWebixAdmin(ModelWebixAdminPermissionsMixin):
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

    enable_button_save_continue_create = None
    enable_button_save_addanother_create = None
    enable_button_save_gotolist_create = None

    enable_button_save_continue_update = None
    enable_button_save_addanother_update = None
    enable_button_save_gotolist_update = None

    # DJANGO WEBIX FORM: OPTION 1
    autocomplete_fields = []
    readonly_fields = []
    fields = None
    exclude = None
    # DJANGO WEBIX FORM: OPTION 2
    form = None
    form_create = None
    form_update = None

    template_form_style = None

    label_width = None

    inlines = []

    errors_on_popup = False

    # LIST SETTINGS
    ordering = None
    actions = []
    list_display = []
    list_display_header = {}  # NEW OVERRIDE HEADER MODALITY
    extra_header = {}  # TO BE REMOVED IN FUTURE
    list_editable = []

    enable_json_loading = True  # changed from the past
    paginate_count_default = 100
    pk_field = None
    title = None
    actions_style = None
    enable_column_copy = True
    model_copy_fields = None
    inlines_copy_fields = None
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'
    enable_actions = True
    remove_disabled_buttons = False

    # permission custom
    only_superuser = False

    # prefix = None
    # def __init__(self, prefix=None):
    #    self.prefix = prefix

    # over

    def is_enable_row_click(self, request):
        return self.enable_row_click

    def get_extra_context(self, view=None, request=None):
        return {}

    def get_label_width(self):
        return getattr(self, 'label_width', None)

    def get_prefix(self):
        return getattr(self, 'prefix', None)

    def get_model_copy_fields(self):
        if self.model_copy_fields is not None:
            return self.model_copy_fields
        else:
            return self.get_form_fields()

    def get_template_form_style(self):
        return self.template_form_style

    def get_url_pattern_list(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        pattern = '%s.%s.list' % info
        if self.get_prefix() not in ['', None]:
            pattern += '.%s' % self.get_prefix()
        return pattern

    def get_url_pattern_create(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        pattern = '%s.%s.create' % info
        if self.get_prefix() not in ['', None]:
            pattern += '.%s' % self.get_prefix()
        return pattern

    def get_url_pattern_update(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        pattern = '%s.%s.update' % info
        if self.get_prefix() not in ['', None]:
            pattern += '.%s' % self.get_prefix()
        return pattern

    def get_url_pattern_delete(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        pattern = '%s.%s.delete' % info
        if self.get_prefix() not in ['', None]:
            pattern += '.%s' % self.get_prefix()
        return pattern

    def get_model_perms(self, request):
        """
        Return a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, ``delete``, and ``view`` mapping to the True/False
        for each of those actions.
        """
        return {
            'add': self.has_add_permission(view=None, request=request),
            'change': self.has_change_permission(view=None, request=request),
            'delete': self.has_delete_permission(view=None, request=request),
            'view': self.has_view_permission(view=None, request=request),
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
                    # VIEW MANAGE BY HERSELF
                    return key
            elif hasattr(_next, 'related_model'):
                _next = _next.related_model._meta.get_field(key)
            else:
                raise Exception('TODO?')
        return _next

    def create_list_display(self, list_display, request=None):
        _fields = []
        for j, field_name in enumerate(list_display):
            if field_name in self.list_display_header:
                _fields.append(self.list_display_header[field_name])  # NEW OVERRIDE HEADER MODALITY
            else:
                model_field = self.get_field_traverse(field_name)
                filter_type = 'icontains'
                format_type = None
                extra_filter_options = ''
                filter_option = 'serverFilter' if self.enable_json_loading else 'textFilter'
                column_template = ''
                editor = ''
                extra_header = ''
                width_adapt = 'fillspace:true' if j == 0 else 'adjust:"all"'
                sort_option = 'server' if self.enable_json_loading else 'string'
                click_action = None
                footer = None
                if type(model_field) == str:
                    header_title = model_field
                else:
                    # if boolean then custom choices
                    header_title = capfirst(model_field.verbose_name)

                if type(model_field) == BooleanField:
                    editor= 'editor:"select",collection: {}_options '.format(field_name)
                    filter_type = ''
                    filter_option = 'serverSelectFilter' if self.enable_json_loading else 'selectFilter'
                    extra_filter_options = ", options:[{id: 'True', value: '" + _('Yes') + "'}, {id: 'False', value: '" + _("No") + "'}] "
                    column_template = ' template:custom_checkbox_yesnonone, '
                elif type(model_field) == DateTimeField:
                    editor= 'editor:"datetime", ' # our custom editor
                    filter_type = 'range'
                    filter_option = 'serverDateRangeFilter' if self.enable_json_loading else 'dateRangeFilter'
                    format_type = 'webix.i18n.fullDateFormatStr'
                    column_template = ' template: function(obj){{if (obj.{field_name}===null) {{return ""}} else {{return this.format(new Date(obj.{field_name})) }} }},'.format(
                        field_name=field_name)
                elif type(model_field) == DateField:
                    #width_adapt = 'width:"85"'
                    editor = 'editor:"date", '
                    filter_type = 'range'
                    filter_option = 'serverDateRangeFilter' if self.enable_json_loading else 'dateRangeFilter'
                    format_type = 'webix.i18n.dateFormatStr'
                elif '__' in field_name:
                    try:
                        _first_field = self.model._meta.get_field(field_name.split('__')[0])
                    except FieldDoesNotExist:
                        pass
                    else:
                        if type(_first_field) == ForeignKey:
                            filter_type = 'iexact'
                            editor = 'editor:"select",collection: {}_options '.format(field_name)
                            filter_option = 'serverRichSelectFilter' if self.enable_json_loading else 'selectFilter'
                            extra_filter_options = ", options: {}_options ".format(field_name)
                # if choices... the same of FK
                else:
                    editor = 'editor:"text", '
                    try:
                        _first_field = self.model._meta.get_field(field_name)
                    except FieldDoesNotExist:
                        pass
                    else:
                        if hasattr(_first_field, 'choices') and _first_field.choices is not None:
                            editor = 'editor:"select",collection: {}_options '.format(field_name)
                            filter_type = 'iexact'
                            filter_option = 'serverRichSelectFilter' if self.enable_json_loading else 'selectFilter'
                            extra_filter_options = ", options: {}_options ".format(field_name)

                if field_name in self.extra_header:  # TO BE REMOVED IN FUTURE
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
                    if 'column_template' in conf_header:
                        column_template = conf_header.get('column_template', '')
                    if 'extra_filter_options' in conf_header:
                        extra_filter_options = conf_header.get('extra_filter_options', '')
                    if 'footer' in conf_header:
                        footer = conf_header.get('footer', None)
                if field_name not in self.list_editable:
                    editor = ''
                field_list = {
                    'field_name': field_name,
                    'datalist_column': '''{{id: "{field_name}",
                header: ["{header_title}", {{content: "{filter}" {extra_filter_options}}}],
                {width_adapt},
                adjustBatch: {adjust_batch},
                sort: "{sort_option}",
                {format_type}
                serverFilterType: "{filter_type}",
                {column_template}
                {editor}
                {extra_header} }}'''.format(
                        field_name=field_name,
                        header_title=header_title,
                        filter=filter_option,
                        format_type=' format: ' + format_type + ', ' if format_type is not None else '',
                        extra_filter_options=extra_filter_options,
                        width_adapt=width_adapt,
                        adjust_batch=self.paginate_count_default,
                        sort_option=sort_option,
                        filter_type=filter_type,
                        column_template=column_template,
                        editor = editor,
                        extra_header=extra_header
                    )
                }
                if footer is not None:
                    field_list.update({'footer': footer})
                if click_action is not None:
                    field_list['click_action'] = click_action
                _fields.append(field_list)
        return _fields

    def get_list_display(self, request=None):
        if type(self.list_display[0]) == str:
            return self.create_list_display(self.list_display, request=request)
        else:
            return self.list_display

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__()

    def __str__(self):
        _str = "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)
        if self.get_prefix() is not None:
            _str += '.%s' % self.get_prefix()
        return _str

    def get_queryset(self, view=None, request=None):
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

    def get_form_class(self, view=None):
        from django_webix.views import WebixCreateView, WebixUpdateView
        _admin = self
        if self.form:
            return self.form
        elif issubclass(type(view), WebixCreateView) and self.form_create is not None:
            return self.form_create
        elif issubclass(type(view), WebixUpdateView) and self.form_update is not None:
            return self.form_update
        else:
            from django_webix.forms import WebixModelForm

            class WebixAdminCreateUpdateForm(WebixModelForm):

                class Meta:
                    localized_fields = ('__all__')
                    model = _admin.model
                    fields = _admin.get_form_fields()

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.readonly_fields = _admin.readonly_fields
                    self.autocomplete_fields = _admin.autocomplete_fields
                    if _admin.get_label_width() is not None:
                        self.label_width = _admin.get_label_width()

            return WebixAdminCreateUpdateForm

    def get_layers(self):
        layers = []
        if getattr(self, 'model', None) is not None:
            layers = get_layers(getattr(self, 'model', None), getattr(self, 'qxs_layers', None))
        return layers

    def get_add_view(self):
        _admin = self
        if self.create_view is not None:
            return self.create_view
        else:
            from django_webix.views import WebixCreateView

            @method_decorator(script_login_required, name='dispatch')
            class WebixAdminCreateView(WebixCreateView):

                if hasattr(_admin, 'dispatch'):
                    def dispatch(self, *args, **kwargs):
                        kwargs.update({'view': self})
                        return _admin.dispatch(*args, **kwargs)

                admin_prefix = _admin.get_prefix()

                def get_view_prefix(self):
                    if self.admin_prefix is not None:
                        return '{}_{}_{}_'.format(self.admin_prefix,
                                                  self.model._meta.app_label,
                                                  self.model._meta.model_name)
                    else:
                        return '{}_{}_'.format(self.model._meta.app_label,
                                               self.model._meta.model_name)

                url_pattern_list = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_list())
                url_pattern_create = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_create())
                url_pattern_update = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_update())
                url_pattern_delete = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_delete())

                model = _admin.model

                def get_form_class(self):
                    return _admin.get_form_class(view=self)

                template_style = _admin.get_template_form_style()
                inlines = _admin.inlines

                if hasattr(_admin, 'response_valid'):
                    def response_valid(self, view=None, success_url=None, **kwargs):
                        return _admin.response_valid(view=self, success_url=success_url, **kwargs)

                if hasattr(_admin, 'get_success_url'):
                    def get_success_url(self, next_step=None):
                        return _admin.get_success_url(view=self, next_step=next_step)

                if hasattr(_admin, 'get_url_create_kwargs'):
                    def get_url_create_kwargs(self):
                        return _admin.get_url_create_kwargs(view=self)

                if hasattr(_admin, 'get_url_create'):
                    def get_url_create(self):
                        return _admin.get_url_create(view=self)

                if hasattr(_admin, 'get_url_update'):
                    def get_url_update(self, obj=None):
                        return _admin.get_url_update(view=self, obj=obj)

                if hasattr(_admin, 'get_url_delete'):
                    def get_url_delete(self, obj=None):
                        return _admin.get_url_delete(view=self, obj=obj)

                if hasattr(_admin, 'get_url_list'):
                    def get_url_list(self):
                        return _admin.get_url_list(view=self)

                if hasattr(_admin, 'get_container_id'):
                    def get_container_id(self, request):
                        return _admin.get_container_id(view=self, request=request)

                if hasattr(_admin, 'get_form'):
                    def get_form(self, form_class=None):
                        return _admin.get_form(view=self, form_class=form_class)

                if hasattr(_admin, 'get_form_kwargs'):
                    def get_form_kwargs(self):
                        return _admin.get_form_kwargs(view=self)

                if hasattr(_admin, 'forms_valid'):
                    def forms_valid(self, form, inlines, **kwargs):
                        return _admin.forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'pre_forms_valid'):
                    def pre_forms_valid(self, form, inlines, **kwargs):
                        return _admin.pre_forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'post_form_save'):
                    def post_form_save(self, form, inlines, **kwargs):
                        return _admin.post_form_save(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'post_forms_valid'):
                    def post_forms_valid(self, form, inlines, **kwargs):
                        return _admin.post_forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'get_initial'):
                    def get_initial(self):
                        return _admin.get_initial(view=self)

                if hasattr(_admin, 'get_inlines'):
                    def get_inlines(self):
                        return _admin.get_inlines(view=self, object=self.object, request=self.request)

                errors_on_popup = _admin.errors_on_popup

                model_copy_fields = _admin.get_model_copy_fields()
                enable_button_save_continue = _admin.enable_button_save_continue_create if _admin.enable_button_save_continue_create is not None else _admin.enable_button_save_continue
                enable_button_save_addanother = _admin.enable_button_save_addanother_create if _admin.enable_button_save_addanother_create is not None else _admin.enable_button_save_addanother
                enable_button_save_gotolist = _admin.enable_button_save_gotolist_create if _admin.enable_button_save_gotolist_create is not None else _admin.enable_button_save_gotolist

                add_permission = _admin.add_permission
                change_permission = _admin.change_permission
                delete_permission = _admin.delete_permission
                view_permission = _admin.view_permission
                view_or_change_permission = _admin.view_or_change_permission
                module_permission = _admin.module_permission

                def has_add_permission(self, request):
                    return _admin.has_add_permission(view=self, request=request)
                def has_change_permission(self, request, obj=None):
                    return _admin.has_change_permission(view=self, request=request, obj=obj)
                def has_delete_permission(self, request, obj=None):
                    return _admin.has_delete_permission(view=self, request=request, obj=obj)
                def has_view_permission(self, request, obj=None):
                    return _admin.has_view_permission(view=self, request=request, obj=obj)

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                def get_info_no_add_permission(self, has_permission, request):
                    return _admin.get_info_no_add_permission(self, has_permission, request)
                def get_info_no_change_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_change_permission(self, has_permission, request, obj=obj)
                def get_info_no_delete_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_delete_permission(self, has_permission, request, obj=obj)
                def get_info_no_view_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_view_permission(self, has_permission, request, obj=obj)

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.add_form_template is not None:
                    template_name = _admin.add_form_template

                def get_queryset(self):
                    return _admin.get_queryset(view=self, request=self.request)

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context.update(_admin.get_extra_context(view=self, request=self.request))
                    return context

            return WebixAdminCreateView

    def get_change_view(self):
        _admin = self
        if self.update_view is not None:
            return self.update_view
        else:
            from django_webix.views import WebixUpdateView

            @method_decorator(script_login_required, name='dispatch')
            class WebixAdminUpdateView(WebixUpdateView):

                if hasattr(_admin, 'dispatch'):
                    def dispatch(self, *args, **kwargs):
                        kwargs.update({'view': self})
                        return _admin.dispatch(*args, **kwargs)

                admin_prefix = _admin.get_prefix()
                def get_view_prefix(self):
                    if self.admin_prefix is not None:
                        return '{}_{}_{}_'.format(self.admin_prefix,
                                                  self.model._meta.app_label,
                                                  self.model._meta.model_name)
                    else:
                        return '{}_{}_'.format(self.model._meta.app_label,
                                               self.model._meta.model_name)

                url_pattern_list = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_list())
                url_pattern_create = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_create())
                url_pattern_update = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_update())
                url_pattern_delete = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_delete())

                model = _admin.model

                def get_form_class(self):
                    return _admin.get_form_class(view=self)

                template_style = _admin.get_template_form_style()
                inlines = _admin.inlines

                if hasattr(_admin, 'response_valid'):
                    def response_valid(self, view=None, success_url=None, **kwargs):
                        return _admin.response_valid(view=self, success_url=success_url, **kwargs)

                if hasattr(_admin, 'get_success_url'):
                    def get_success_url(self, next_step=None):
                        return _admin.get_success_url(view=self, next_step=next_step)

                if hasattr(_admin, 'get_url_create_kwargs'):
                    def get_url_create_kwargs(self):
                        return _admin.get_url_create_kwargs(view=self)

                if hasattr(_admin, 'get_url_create'):
                    def get_url_create(self):
                        return _admin.get_url_create(view=self)

                if hasattr(_admin, 'get_url_update'):
                    def get_url_update(self, obj=None):
                        return _admin.get_url_update(view=self, obj=obj)

                if hasattr(_admin, 'get_url_delete'):
                    def get_url_delete(self, obj=None):
                        return _admin.get_url_delete(view=self, obj=obj)

                if hasattr(_admin, 'get_url_list'):
                    def get_url_list(self):
                        return _admin.get_url_list(view=self)

                if hasattr(_admin, 'get_container_id'):
                    def get_container_id(self, request):
                        return _admin.get_container_id(view=self, request=request)

                if hasattr(_admin, 'get_form'):
                    def get_form(self, form_class=None):
                        return _admin.get_form(view=self, form_class=form_class)

                if hasattr(_admin, 'get_form_kwargs'):
                    def get_form_kwargs(self):
                        return _admin.get_form_kwargs(view=self)

                if hasattr(_admin, 'forms_valid'):
                    def forms_valid(self, form, inlines, **kwargs):
                        return _admin.forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'pre_forms_valid'):
                    def pre_forms_valid(self, form, inlines, **kwargs):
                        return _admin.pre_forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'post_form_save'):
                    def post_form_save(self, form, inlines, **kwargs):
                        return _admin.post_form_save(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'post_forms_valid'):
                    def post_forms_valid(self, form, inlines, **kwargs):
                        return _admin.post_forms_valid(view=self, form=form, inlines=inlines, **kwargs)

                if hasattr(_admin, 'get_initial'):
                    def get_initial(self):
                        return _admin.get_initial(view=self)

                if hasattr(_admin, 'get_inlines'):
                    def get_inlines(self):
                        return _admin.get_inlines(view=self, object=self.object, request=self.request)

                errors_on_popup = _admin.errors_on_popup

                model_copy_fields = _admin.get_model_copy_fields()
                enable_button_save_continue = _admin.enable_button_save_continue_update if _admin.enable_button_save_continue_update is not None else _admin.enable_button_save_continue
                enable_button_save_addanother = _admin.enable_button_save_addanother_update if _admin.enable_button_save_addanother_update is not None else _admin.enable_button_save_addanother
                enable_button_save_gotolist = _admin.enable_button_save_gotolist_update if _admin.enable_button_save_gotolist_update is not None else _admin.enable_button_save_gotolist

                add_permission = _admin.add_permission
                change_permission = _admin.change_permission
                delete_permission = _admin.delete_permission
                view_permission = _admin.view_permission
                view_or_change_permission = _admin.view_or_change_permission
                module_permission = _admin.module_permission

                def has_add_permission(self, request):
                    return _admin.has_add_permission(view=self, request=request)
                def has_change_permission(self, request, obj=None):
                    return _admin.has_change_permission(view=self, request=request, obj=obj)
                def has_delete_permission(self, request, obj=None):
                    return _admin.has_delete_permission(view=self, request=request, obj=obj)
                def has_view_permission(self, request, obj=None):
                    return _admin.has_view_permission(view=self, request=request, obj=obj)

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                def get_info_no_add_permission(self, has_permission, request):
                    return _admin.get_info_no_add_permission(self, has_permission, request)
                def get_info_no_change_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_change_permission(self, has_permission, request, obj=obj)
                def get_info_no_delete_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_delete_permission(self, has_permission, request, obj=obj)
                def get_info_no_view_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_view_permission(self, has_permission, request, obj=obj)

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.change_form_template is not None:
                    template_name = _admin.change_form_template

                def get_queryset(self):
                    return _admin.get_queryset(view=self,
                                               request=self.request)

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context.update(_admin.get_extra_context(view=self,
                                                            request=self.request
                                                            ))
                    return context

            return WebixAdminUpdateView

    def get_delete_view(self):
        _admin = self
        if self.delete_view is not None:
            return self.delete_view
        else:
            from django_webix.views import WebixDeleteView

            @method_decorator(script_login_required, name='dispatch')
            class WebixAdminDeleteView(WebixDeleteView):

                if hasattr(_admin, 'dispatch'):
                    def dispatch(self, *args, **kwargs):
                        kwargs.update({'view': self})
                        return _admin.dispatch(*args, **kwargs)

                admin_prefix = _admin.get_prefix()
                def get_view_prefix(self):
                    if self.admin_prefix is not None:
                        return '{}_{}_{}_'.format(self.admin_prefix,
                                                  self.model._meta.app_label,
                                                  self.model._meta.model_name)
                    else:
                        return '{}_{}_'.format(self.model._meta.app_label,
                                               self.model._meta.model_name)

                url_pattern_list =   '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_list())
                url_pattern_create = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_create())
                url_pattern_update = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_update())
                url_pattern_delete = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_delete())

                add_permission = _admin.add_permission
                change_permission = _admin.change_permission
                delete_permission = _admin.delete_permission
                view_permission = _admin.view_permission
                view_or_change_permission = _admin.view_or_change_permission
                module_permission = _admin.module_permission

                def has_add_permission(self, request):
                    return _admin.has_add_permission(view=self, request=request)
                def has_change_permission(self, request, obj=None):
                    return _admin.has_change_permission(view=self, request=request, obj=obj)
                def has_delete_permission(self, request, obj=None):
                    return _admin.has_delete_permission(view=self, request=request, obj=obj)
                def has_view_permission(self, request, obj=None):
                    return _admin.has_view_permission(view=self, request=request, obj=obj)

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                def get_info_no_add_permission(self, has_permission, request):
                    return _admin.get_info_no_add_permission(self, has_permission, request)
                def get_info_no_change_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_change_permission(self, has_permission, request, obj=obj)
                def get_info_no_delete_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_delete_permission(self, has_permission, request, obj=obj)
                def get_info_no_view_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_view_permission(self, has_permission, request, obj=obj)

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                model = _admin.model

                if hasattr(_admin, 'response_valid'):
                    def response_valid(self, view=None, success_url=None, **kwargs):
                        return _admin.response_valid(view=self, success_url=success_url, **kwargs)

                if hasattr(_admin, 'get_container_id'):
                    def get_container_id(self, request):
                        return _admin.get_container_id(view=self, request=request)

                if hasattr(_admin, 'get_success_url'):
                    def get_success_url(self, next_step=None):
                        return _admin.get_success_url(view=self, next_step=next_step)

                if hasattr(_admin, 'get_url_create_kwargs'):
                    def get_url_create_kwargs(self):
                        return _admin.get_url_create_kwargs(view=self)

                if hasattr(_admin, 'get_url_create'):
                    def get_url_create(self):
                        return _admin.get_url_create(view=self)

                if hasattr(_admin, 'get_url_update'):
                    def get_url_update(self, obj=None):
                        return _admin.get_url_update(view=self, obj=obj)

                if hasattr(_admin, 'get_url_delete'):
                    def get_url_delete(self, obj=None):
                        return _admin.get_url_delete(view=self, obj=obj)

                if hasattr(_admin, 'get_url_list'):
                    def get_url_list(self):
                        return _admin.get_url_list(view=self)

                if _admin.delete_template is not None:
                    template_name = _admin.delete_template

                def get_queryset(self):
                    return _admin.get_queryset(view=self,
                                               request=self.request)

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context.update(_admin.get_extra_context(view=self,
                                                            request=self.request))
                    return context

            return WebixAdminDeleteView

    def get_list_view(self):
        _admin = self
        if self.list_view is not None:
            return self.list_view
        else:
            from django_webix.views import WebixListView

            @method_decorator(script_login_required, name='dispatch')
            class WebixAdminListView(WebixListView):

                if hasattr(_admin, 'dispatch'):
                    def dispatch(self, *args, **kwargs):
                        kwargs.update({'view': self})
                        return _admin.dispatch(*args, **kwargs)

                admin_prefix = _admin.get_prefix()
                def get_view_prefix(self):
                    if self.admin_prefix is not None:
                        return '{}_{}_{}_'.format(self.admin_prefix,
                                                  self.model._meta.app_label,
                                                  self.model._meta.model_name)
                    else:
                        return '{}_{}_'.format(self.model._meta.app_label,
                                               self.model._meta.model_name)

                url_pattern_list =   '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_list())
                url_pattern_create = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_create())
                url_pattern_update = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_update())
                url_pattern_delete = '{}:{}'.format(self.admin_site.urls_namespace, _admin.get_url_pattern_delete())

                adjust_row_height = False

                model = _admin.model
                pk_field = _admin.pk_field
                order_by = _admin.ordering
                actions = _admin.actions

                if hasattr(_admin, 'get_actions'):
                    def get_actions(self):
                        return _admin.get_actions(view=self)

                if hasattr(_admin, 'get_choices_filters'):
                    def get_choices_filters(self):
                        return _admin.get_choices_filters(view=self)

                errors_on_popup = _admin.errors_on_popup

                enable_json_loading = _admin.enable_json_loading
                paginate_count_default = _admin.paginate_count_default
                title = _admin.title
                actions_style = _admin.actions_style
                enable_column_copy = _admin.enable_column_copy
                enable_column_delete = _admin.enable_column_delete
                enable_row_click = _admin.enable_row_click
                is_enable_row_click = _admin.is_enable_row_click
                type_row_click = _admin.type_row_click
                enable_actions = _admin.enable_actions

                add_permission = _admin.add_permission
                change_permission = _admin.change_permission
                delete_permission = _admin.delete_permission
                view_permission = _admin.view_permission
                view_or_change_permission = _admin.view_or_change_permission
                module_permission = _admin.module_permission

                def has_add_permission(self, request):
                    return _admin.has_add_permission(view=self, request=request)
                def has_change_permission(self, request, obj=None):
                    return _admin.has_change_permission(view=self, request=request, obj=obj)
                def has_delete_permission(self, request, obj=None):
                    return _admin.has_delete_permission(view=self, request=request, obj=obj)
                def has_view_permission(self, request, obj=None):
                    return _admin.has_view_permission(view=self, request=request, obj=obj)

                get_failure_add_related_objects = _admin.get_failure_add_related_objects
                get_failure_change_related_objects = _admin.get_failure_change_related_objects
                get_failure_delete_related_objects = _admin.get_failure_delete_related_objects
                get_failure_view_related_objects = _admin.get_failure_view_related_objects

                def get_info_no_add_permission(self, has_permission, request):
                    return _admin.get_info_no_add_permission(self, has_permission, request)
                def get_info_no_change_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_change_permission(self, has_permission, request, obj=obj)
                def get_info_no_delete_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_delete_permission(self, has_permission, request, obj=obj)
                def get_info_no_view_permission(self, has_permission, request, obj=None):
                    return _admin.get_info_no_view_permission(self, has_permission, request, obj=obj)

                remove_disabled_buttons = _admin.remove_disabled_buttons
                get_layers = _admin.get_layers

                if _admin.change_list_template is not None:
                    template_name = _admin.change_list_template

                if hasattr(_admin, 'get_container_id'):
                    def get_container_id(self, request):
                        return _admin.get_container_id(view=self, request=request)

                if hasattr(_admin, 'get_url_create_kwargs'):
                    def get_url_create_kwargs(self):
                        return _admin.get_url_create_kwargs(view=self)

                if hasattr(_admin, 'get_url_create'):
                    def get_url_create(self):
                        return _admin.get_url_create(view=self)

                if hasattr(_admin, 'get_url_update'):
                    def get_url_update(self, obj=None):
                        return _admin.get_url_update(view=self, obj=obj)

                if hasattr(_admin, 'get_url_delete'):
                    def get_url_delete(self, obj=None):
                        return _admin.get_url_delete(view=self, obj=obj)

                if hasattr(_admin, 'get_url_list'):
                    def get_url_list(self):
                        return _admin.get_url_list(view=self)

                def get_initial_queryset(self):
                    return _admin.get_queryset(view=self,
                                               request=self.request)

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context.update(_admin.get_extra_context(view=self,
                                                            request=self.request))
                    return context

                @property
                def fields_editable(self):
                    return _admin.list_editable

                # full mode
                @property
                def fields(self):
                    if len(_admin.list_display) > 0:
                        return _admin.get_list_display(request=self.request)
                    else:
                        return None

            return WebixAdminListView

    enable_url_list = True
    enable_url_create = True
    enable_url_delete = True
    enable_url_update = True

    def get_urls(self):
        _prefix = self.get_prefix()
        if _prefix not in [None, '']:
            _prefix += '/'
        else:
            _prefix = ''

        _urls = []
        if self.enable_url_list == True:
            _urls.append(path(_prefix+'', self.get_list_view().as_view(), name=self.get_url_pattern_list()))
        if self.enable_url_create == True:
            _urls.append(path(_prefix+'create/', self.get_add_view().as_view(), name=self.get_url_pattern_create()))
        if self.enable_url_delete == True:
            _urls.append(path(_prefix+'<int:pk>/delete/', self.get_delete_view().as_view(), name=self.get_url_pattern_delete()))
        if self.enable_url_update == True:
            _urls.append(path(_prefix+'<int:pk>/update/', self.get_change_view().as_view(), name=self.get_url_pattern_update()))
        return _urls

    @property
    def urls(self):
        return self.get_urls()
