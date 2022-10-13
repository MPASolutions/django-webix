Admin Model
=====

Parameters
~~~~~~~~~~~

Create the files (e.g. <app_name>/admin_webix.py).
The main idea is that many properties and functions that are on views are moved (with some other patameters) directly
on admin class.
Here there is an example of main list of parameters and functions that can be override.

.. code-block:: python

    from <project_name>.admin_webix import site
    from django_webix import admin_webix as admin

    @admin.register(ModelName, site=site)
    class CustomModelWebixAdmin(admin.ModelWebixAdmin):
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

        # INLINES
        inlines = []

        # FORM STYLE AND RESPONSE
        template_form_style = None
        label_width = None
        errors_on_popup = False

        # LIST SETTINGS
        ordering = None
        actions = []
        list_display = []
        list_display_header = {}  # NEW OVERRIDE HEADER MODALITY
        list_editable = []

        enable_json_loading = True
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

        def is_enable_row_click(self, request):
            return self.enable_row_click

        # GIS
        qxs_layers = []

        # utils
        def get_prefix(self):
            return getattr(self, 'prefix', None)

        def get_extra_context(self, view=None, request=None):
            return {}

        def get_queryset(self, view=None, request=None):
            return self.model._default_manager.all()

        # permission custom

        only_superuser = False

        def has_add_permission(self, request, view=None):
            ...
        def has_change_permission(self, request, obj=None, view=None):
            ...
        def has_delete_permission(self, request, obj=None, view=None):
            ...
        def has_view_permission(self, request, obj=None, view=None):
            ...

        def get_failure_add_related_objects(self, request):
            return []
        def get_failure_change_related_objects(self, request):
            return []
        def get_failure_delete_related_objects(self, request):
            return []
        def get_failure_view_related_objects(self, request):
            return []

        def get_info_no_add_permission(self, has_permission, request, view=None):
            ...
        def get_info_no_change_permission(self, has_permission, request, obj=None, view=None):
            ...
        def get_info_no_delete_permission(self, has_permission, request, obj=None, view=None):
            ...
        def get_info_no_view_permission(self, has_permission, request, obj=None, view=None):
            ...

        def get_model_perms(self, request, view=None):
            return {
                'add': self.has_add_permission(request, view=view),
                'change': self.has_change_permission(request, view=view),
                'delete': self.has_delete_permission(request, view=view),
                'view': self.has_view_permission(request, view=view),
            }

        def has_module_permission(self, request):
            if self.only_superuser:
                if request.user.is_superuser:
                    return True
                return False
            return super().has_module_permission(request)


        def get_add_view(self): # for completly override
            ...
        def get_change_view(self): # for completly override
            ...
        def get_delete_view(self): # for completly override
            ...
        def get_list_view(self): # for completly override
            ...

        # URLS

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

        # EXTRA functions
        # in all these functions is added view as parameter
        # you can check it with something like this: if issubclass(type(view), WebixCreateView):
        # if request is not a parameter you can access ot it by view.request NOT self.request

        def dispatch(self, *args, **kwargs)
            view = kwargs.pop('view')
            return super(view.__class__).dispatch(*args, **kwargs)

        def get_url_create_kwargs(self, view=None)
            return super(view.__class__).get_url_create_kwargs()

        def get_url_create(self, view=None)
            return super(view.__class__).get_url_create()

        def get_url_update(self, view=None, obj=None)
            return super(view.__class__).get_url_update(obj=obj)

        def get_url_delete(self, view=None, obj=None)
            return super(view.__class__).get_url_delete(obj=obj)

        def get_url_list(self, view=None)
            return super(view.__class__).get_url_list()

        def get_container_id(self, view, request):

        def get_form(self, view, form_class):

        def get_form_kwargs(self, view):

        def pre_forms_valid(self, view, form, inlines, **kwargs):

        def post_form_valid(self, view, form, inlines, **kwargs):

        def post_forms_valid(self, view, form, inlines, **kwargs):

        def get_initial(self, view):

        def get_inlines(self, view, object, request):

        def get_actions(self, view):

