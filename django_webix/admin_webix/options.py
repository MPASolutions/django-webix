from django.db.models import AutoField
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

    enable_json_loading = False

    title = None
    actions_style = None
    enable_column_copy = True
    enable_column_delete = True
    enable_row_click = True
    type_row_click = 'single'
    enable_actions = True

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

    def get_field_traverse(self, path):
        _next = self.model
        for j, key in enumerate(path.split('__')):
            if j == 0:
                _next = _next._meta.get_field(key)
            elif hasattr(_next, 'related_model'):
                _next = _next.related_model._meta.get_field(key)
            else:
                raise Exception('TODO?')
        return _next

    def get_list_display(self):
        _fields = []
        for j, field_name in enumerate(self.list_display):
            model_field = self.get_field_traverse(field_name)
            _fields.append({
                'field_name': field_name,
                'datalist_column': '''{{id: "{field_name}", header: ["{header_title}", {{content: "textFilter"}}], {width_adapt}, sort: "string" }}'''.format(
                    field_name=field_name,
                    header_title=capfirst(model_field.verbose_name),
                    width_adapt='fillspace:true' if j == 0 else 'adjust:"all"',
                )
            })
        return _fields

    def __init__(self, model, admin_site):
        self.model = model
        self.opts = model._meta
        self.admin_site = admin_site
        super().__init__()

    def __str__(self):
        return "%s.%s" % (self.model._meta.app_label, self.__class__.__name__)

    def get_queryset(self):
        return self.model._default_manager.all()

    def get_form_fields(self):
        _fields = []
        for _field in self.model._meta.fields:
            if type(_field) != AutoField and \
                (self.exclude is None or _field.name not in self.exclude) and \
                _field.editable is True:
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

                def get_queryset(self):
                    return _admin.get_queryset()

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

                def get_queryset(self):
                    return _admin.get_queryset()

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

                model = _admin.model

                def get_queryset(self):
                    return _admin.get_queryset()

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

                def get_queryset(self):
                    return super().get_queryset(initial_queryset=_admin.get_queryset())

                def get_fields(self):
                    return _admin.get_list_display()

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
