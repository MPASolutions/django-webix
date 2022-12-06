Admin Model
===========

Example
-------

Create the files (e.g. <app_name>/dwadmin.py).
The main idea is that many properties and functions that are on views are moved (with some other patameters) directly
on admin class.
Here there is an example of main list of parameters and functions that can be override.

.. code-block:: python

    from <project_name>.dwadmin import site
    from django_webix.contrib.admin import dwadmin as admin

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

        def has_add_permission(self, view, request):
            ...
        def has_change_permission(self, view, request, obj=None):
            ...
        def has_delete_permission(self, view, request, obj=None):
            ...
        def has_view_permission(self, view, request, obj=None):
            ...

        def get_failure_add_related_objects(self, request):
            return []
        def get_failure_change_related_objects(self, request):
            return []
        def get_failure_delete_related_objects(self, request):
            return []
        def get_failure_view_related_objects(self, request):
            return []

        def get_info_no_add_permission(self, view, has_permission, request):
            ...
        def get_info_no_change_permission(self, view, has_permission, request, obj=None):
            ...
        def get_info_no_delete_permission(self, view, has_permission, request, obj=None):
            ...
        def get_info_no_view_permission(self, view, has_permission, request, obj=None):
            ...

        def get_model_perms(self, request, view=None):
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

        def response_valid(self, view=None, success_url=None, **kwargs):
            return super(view.__class__).response_valid(success_url=success_url, **kwargs)

        def get_container_id(self, view, request):

        def get_form(self, view, form_class):

        def get_form_kwargs(self, view):

        def pre_forms_valid(self, view, form, inlines, **kwargs):

        def post_form_valid(self, view, form, inlines, **kwargs):

        def post_forms_valid(self, view, form, inlines, **kwargs):

        def get_initial(self, view):

        def get_inlines(self, view, object, request):

        def get_actions(self, view):

Custom view
-----------

For each model registration there are a 4 views: CreateView, UpdateView, DeleteView and ListView.
You can define directly a CustomView for each view

.. code-block:: python

        create_view = None
        update_view = None
        delete_view = None
        list_view = None

or access to a super() costructor by get_XXX_view.

.. code-block:: python

        def get_add_view(self):
        def get_change_view(self):
        def get_delete_view(self):
        def get_list_view(self):

Templates
---------

For each 4 views is possibile to set custom JS template

.. code-block:: python

    add_form_template = None
    change_form_template = None
    change_list_template = None
    delete_template = None

Also you can set specific container to move loading in extra webix template areas.

.. code-block:: python

    def get_container_id(self, view, request):

Object / Queryset
-----------------

Each view works on instances. Force queryset is the method that for example based on request can
guarantee to check if and user can access to data or not.

.. code-block:: python

    ordering = None
    def get_queryset(self, view=None, request=None):
        return self.model._default_manager.all()

For ListView you can also override PK key.

.. code-block:: python

    pk_field = None

Dispatch
--------

To not override standard dispatch method, view parameter is injected by kwargs. In this way you can fully managed dispatch of each type of view.

.. code-block:: python

    def dispatch(self, *args, **kwargs)
    view = kwargs.pop('view')
    return super(view.__class__).dispatch(*args, **kwargs)

Permissions
-----------

Admin area works expecially with database data. There is a fully support for permission management.

.. code-block:: python

    only_superuser = False

    def has_add_permission(self, view, request):
        ...
    def has_change_permission(self, view, request, obj=None):
        ...
    def has_delete_permission(self, view, request, obj=None):
        ...
    def has_view_permission(self, view, request, obj=None):
        ...

    def get_failure_add_related_objects(self, request):
        return []
    def get_failure_change_related_objects(self, request):
        return []
    def get_failure_delete_related_objects(self, request):
        return []
    def get_failure_view_related_objects(self, request):
        return []

    def get_info_no_add_permission(self, view, has_permission, request):
        ...
    def get_info_no_change_permission(self, view, has_permission, request, obj=None):
        ...
    def get_info_no_delete_permission(self, view, has_permission, request, obj=None):
        ...
    def get_info_no_view_permission(self, view, has_permission, request, obj=None):
        ...

    def get_model_perms(self, request):
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

GIS layer support
-----------------

Mpa Solutions soc coop and Enogis srl have their own GIS module.
In this way is possibile to assign qxs_layers to a ModelAdmin to better interactive support.

.. code-block:: python

    qxs_layers = []

Buttons
-------

In all views there are buttons. If you disable some of then is possibile to remove it by this settings.

.. code-block:: python

    remove_disabled_buttons

Multiple model admin registration
---------------------------------

If if needed multiple Model registration you have to pass to register decorato a specific prefix for each registration.

.. code-block:: python

    prefix
    def get_prefix(self):
        return getattr(self, 'prefix', None)

Context view
------------

It's possibile to set an extra context when is required into a specific or all views.

.. code-block:: python

    def get_extra_context(self, view=None, request=None):
        return {}

Buttons save in UpdateView and CreateView
-----------------------------------------

Into UpdateView and CreateView is possibile to show/hide each of 3 main save buttons.

.. code-block:: python

        enable_button_save_continue = True
        enable_button_save_addanother = True
        enable_button_save_gotolist = True

        enable_button_save_continue_create = None
        enable_button_save_addanother_create = None
        enable_button_save_gotolist_create = None

        enable_button_save_continue_update = None
        enable_button_save_addanother_update = None
        enable_button_save_gotolist_update = None

Form/Inline in UpdateView and CreateView
----------------------------------------

In UpdateView and CreateView is possibile to set custom form.

.. code-block:: python

        form = None
        form_create = None
        form_update = None

or like standard django admin give all fields and caracteristics.

.. code-block:: python

        autocomplete_fields = []
        readonly_fields = []
        fields = None
        exclude = None

also you can set some inlines:

.. code-block:: python

        inlines = []

You can customizate also form with width of label and style of form.

.. code-block:: python

        template_form_style = None
        label_width = None

When you want block user on errors you can show these into a popup with a read confirm button.

.. code-block:: python

    errors_on_popup = False

In terms of form support for CreateView and UpdateView is possibile override form and inlines creation and data insert.

.. code-block:: python

        def get_form(self, view, form_class):

        def get_form_kwargs(self, view):

        def get_initial(self, view):

        def get_inlines(self, view, object, request):


Valid sequentiality UpdateView and CreateView
---------------------------------------------

Some extra function are available for better interact with complete save process.

.. code-block:: python

        def pre_forms_valid(self, view, form, inlines, **kwargs):

        def post_form_valid(self, view, form, inlines, **kwargs):

        def post_forms_valid(self, view, form, inlines, **kwargs):


Valid sequentiality DeleteView
------------------------------

Some extra function are available for better interact with complete delete process.

.. code-block:: python

    def pre_delete_valid(self, **kwargs):
        django_webix_view_pre_delete.send(sender=self, instance=self.object)

    def post_delete_valid(self, **kwargs):
        django_webix_view_post_delete.send(sender=self, instance=self.copied_object)


Response valid for DeleteView, UpdateViev and CreateView
--------------------------------------------------------

After valid operation is possibile to customize the response.

.. code-block:: python

    def response_valid(self, view=None, success_url=None, **kwargs):
        return super(view.__class__).response_valid(success_url=success_url, **kwargs)

List columns
------------

Main List settings are the same that you can see into django-admin standard for column definition.

.. code-block:: python

    list_display = []
    list_editable = []

It's also possibile force header template by

.. code-block:: python

    list_display_header = {}

List actions
------------

Like for generical ListView is possibile to fully manage actions.

.. code-block:: python

    enable_actions = True
    actions = []
    actions_style = None
    def get_actions(self, view):

List data loading
-----------------

Admin support fully ListView paging.

.. code-block:: python

    enable_json_loading = True
    paginate_count_default = 100

List rows and columns
---------------------

It's possibile to manage function on columns as Copy and Delete buttons and you can also define how rows are selected.

.. code-block:: python

        enable_column_copy = True
        model_copy_fields = None
        inlines_copy_fields = None

        enable_column_delete = True

        enable_row_click = True
        type_row_click = 'single'
        def is_enable_row_click(self, request):
            return self.enable_row_click

Urls
----

There is a complete set of functions for manage urls.

You can enable or disable urls.

.. code-block:: python

    enable_url_list = True
    enable_url_create = True
    enable_url_delete = True
    enable_url_update = True

Or if you want add others urls on a ModelAdmin registration you can override get_urls.

.. code-block:: python

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

Or if you want override standard path you can override functions that get pattern urls.

.. code-block:: python

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


List extra config
-----------------

It's possibile to set header title for ListView.

.. code-block:: python

    title = None
