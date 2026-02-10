Views
=====

django-webix provides a set of class-based views that integrate with the `Webix <https://webix.com>`_
UI library. These views extend Django's standard generic views with Webix-specific rendering,
permissions, URL management, and JavaScript template generation.

.. code-block:: python

    from django_webix.views import (
        WebixCreateView,
        WebixDeleteView,
        WebixListView,
        WebixUpdateView,
    )
    from django_webix.views.generic.base import WebixFormView, WebixTemplateView


WebixTemplateView
-----------------

A base template view for rendering Webix UI components. Use it for custom pages that don't map to
a Django model (dashboards, pivot tables, etc.).

.. code-block:: python

    from django_webix.views.generic.base import WebixTemplateView

    class DashboardView(WebixTemplateView):
        template_name = 'myapp/dashboard.html'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['stats'] = compute_stats()
            return context

**Overridable methods:**

- ``get_container_id(request)`` - Returns ``settings.WEBIX_CONTAINER_ID`` by default
- ``get_overlay_container_id(request)`` - Returns ``settings.WEBIX_OVERLAY_CONTAINER_ID``


WebixFormView
-------------

A view for displaying and processing ``WebixForm`` instances (non-model forms). Renders using a
Webix JS template and handles form submission.

.. code-block:: python

    from django.utils.decorators import method_decorator
    from django_webix.utils.decorators import script_login_required
    from django_webix.views.generic.base import WebixFormView
    from myapp.forms import FilterForm

    @method_decorator(script_login_required, name='dispatch')
    class FilterView(WebixFormView):
        form_class = FilterForm
        template_name = 'django_webix/generic/form.js'

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['queryset'] = MyModel.objects.filter(active=True)
            return kwargs

        def get_url_send(self):
            return reverse('myapp.filter')

        def get_success_url(self):
            return reverse('myapp.results')

        def form_valid(self, form):
            # Process the form data
            results = process_filter(form.cleaned_data)
            return HttpResponseRedirect(self.get_success_url())

**Key attributes:**

- ``form_class`` - The form class to use
- ``template_name`` - Defaults to ``'django_webix/generic/form.js'``
- ``url_pattern_send`` - URL pattern name for form submission


WebixListView
-------------

The primary view for displaying model data in a Webix datatable with server-side filtering,
sorting, pagination, and actions.

.. code-block:: python

    from django_webix.views import WebixListView
    from myapp.models import Product

    class ProductListView(WebixListView):
        model = Product

**Class attributes:**

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Attribute
     - Default
     - Description
   * - ``model``
     -
     - The Django model to display
   * - ``pk_field``
     - ``None``
     - Primary key field name (defaults to ``'id'``)
   * - ``fields``
     - ``None``
     - List of field/column definitions (see below)
   * - ``order_by``
     - ``None``
     - Default ordering tuple, e.g., ``('-created_at',)``
   * - ``actions``
     - ``[]``
     - List of action functions (e.g., ``[multiple_delete_action]``)
   * - ``footer``
     - ``True``
     - Enable footer row (for aggregations)
   * - ``enable_json_loading``
     - ``False``
     - Enable server-side pagination (AJAX). Set to ``True`` for large datasets
   * - ``paginate_count_default``
     - ``100``
     - Number of rows per page
   * - ``paginate_start_default``
     - ``0``
     - Starting index
   * - ``paginate_count_key``
     - ``'count'``
     - GET/POST parameter name for page size
   * - ``paginate_start_key``
     - ``'start'``
     - GET/POST parameter name for start index
   * - ``template_name``
     - ``'django_webix/generic/list.js'``
     - The JavaScript template
   * - ``title``
     - ``None``
     - List title (defaults to model's ``verbose_name_plural``)
   * - ``actions_style``
     - ``None``
     - Style for action buttons: ``'buttons'`` or ``'select'``
   * - ``enable_column_webgis``
     - ``True``
     - Show WebGIS map column (requires ``django_webix_leaflet``)
   * - ``enable_column_copy``
     - ``True``
     - Show copy/duplicate column
   * - ``enable_column_delete``
     - ``True``
     - Show delete column
   * - ``enable_row_click``
     - ``True``
     - Enable navigating to update view on row click
   * - ``type_row_click``
     - ``'single'``
     - Click type: ``'single'`` or ``'double'``
   * - ``enable_actions``
     - ``True``
     - Show actions toolbar
   * - ``fields_editable``
     - ``[]``
     - List of field names editable directly in the list
   * - ``adjust_row_height``
     - ``False``
     - Adjust row height to content
   * - ``header_rows``
     - ``2``
     - Number of header rows (label + filter)
   * - ``errors_on_popup``
     - ``False``
     - Show errors in popup instead of inline

Fields and Filters
~~~~~~~~~~~~~~~~~~

The ``fields`` attribute defines the columns and their server-side filter behavior. Each entry is a
dict with ``field_name``, ``datalist_column``, and optionally ``footer`` and ``click_action``.

**Text filter** (``icontains``):

.. code-block:: python

    {
        'field_name': 'name',
        'datalist_column': '{id: "name", serverFilterType: "icontains", '
            'header: ["Name", {content: "serverFilter"}], fillspace: true, sort: "server"}'
    }

**Number filter** (``numbercompare`` - supports operators like ``<=5``, ``>10``):

.. code-block:: python

    {
        'field_name': 'price',
        'footer': Sum('price'),
        'datalist_column': '{id: "price", serverFilterType: "numbercompare", '
            'header: ["Price", {content: "numberFilter"}], '
            'css: {"text-align": "right"}, adjust: "all", sort: "server"}'
    }

**FK/Select filter** (``exact`` with options):

.. code-block:: python

    {
        'field_name': 'category__name',
        'field_pk': 'category__pk',
        'datalist_column': '{id: "category__name", serverFilterType: "exact", '
            'header: ["Category", {content: "serverSelectFilter", '
            'options: category__name_options}], adjust: "all", sort: "server"}'
    }

**Date range filter** (``range``):

.. code-block:: python

    {
        'field_name': 'created_at',
        'datalist_column': '{id: "created_at", serverFilterType: "range", '
            'header: ["Created", {content: "serverDateRangeFilter"}], '
            'adjust: "all", sort: "server"}'
    }

**Boolean filter** (with Yes/No options):

.. code-block:: python

    {
        'field_name': 'is_active',
        'datalist_column': '{id: "is_active", serverFilterType: "exact", '
            'template: custom_checkbox_yesnonone, '
            'header: ["Active", {content: "serverSelectFilter", '
            'options: [{id: "True", value: "Yes"}, {id: "False", value: "No"}]}], '
            'adjust: "all", sort: "server"}'
    }

**Custom click action:**

.. code-block:: python

    {
        'field_name': 'code',
        'click_action': 'open_detail(el["id"]);',
        'datalist_column': '{id: "code", header: ["Code", {content: "serverFilter"}], '
            'fillspace: true, sort: "server"}'
    }

**Footer with aggregations:**

Use Django aggregation functions (``Sum``, ``Count``, ``Avg``, etc.) in the ``footer`` key:

.. code-block:: python

    from django.db.models import Sum, Count

    fields = [
        {
            'field_name': 'amount',
            'footer': Sum('amount'),
            'datalist_column': '...'
        },
        {
            'field_name': 'id',
            'footer': Count('id'),
            'datalist_column': '...'
        },
    ]

Overridable Methods
~~~~~~~~~~~~~~~~~~~

**``get_initial_queryset()``** - Customize the base queryset:

.. code-block:: python

    def get_initial_queryset(self):
        return super().get_initial_queryset().filter(
            organization=self.request.user.organization
        )

**``get_objects_datatable()``** - Customize the data returned to the template:

.. code-block:: python

    def get_objects_datatable(self):
        qs = self.get_queryset()
        # Custom processing...
        return list(qs.values('id', 'name', 'computed_value'))

**``get_fields()``** - Dynamically modify fields:

.. code-block:: python

    def get_fields(self, fields=None):
        _fields = super().get_fields(fields)
        if not self.request.user.is_superuser:
            _fields = [f for f in _fields if f['field_name'] != 'internal_code']
        return _fields

**Complete ListView example:**

.. code-block:: python

    from django.db.models import Sum
    from django_webix.views import WebixListView
    from django_webix.views.generic.actions import multiple_delete_action
    from myapp.models import Invoice

    class InvoiceListView(WebixListView):
        model = Invoice
        enable_json_loading = True
        paginate_count_default = 50
        order_by = ('-date', '-number')
        actions = [multiple_delete_action]
        enable_column_copy = True
        enable_column_delete = True

        fields = [
            {
                'field_name': 'number',
                'datalist_column': '{id: "number", serverFilterType: "icontains", '
                    'header: ["Number", {content: "serverFilter"}], '
                    'fillspace: true, sort: "server"}'
            },
            {
                'field_name': 'date',
                'datalist_column': '{id: "date", serverFilterType: "range", '
                    'header: ["Date", {content: "serverDateRangeFilter"}], '
                    'adjust: "all", sort: "server"}'
            },
            {
                'field_name': 'customer__name',
                'field_pk': 'customer__pk',
                'datalist_column': '{id: "customer__name", serverFilterType: "exact", '
                    'header: ["Customer", {content: "serverSelectFilter", '
                    'options: customer__name_options}], adjust: "all", sort: "server"}'
            },
            {
                'field_name': 'total',
                'footer': Sum('total'),
                'datalist_column': '{id: "total", serverFilterType: "numbercompare", '
                    'header: ["Total", {content: "numberFilter"}], '
                    'css: {"text-align": "right"}, adjust: "all", sort: "server"}'
            },
        ]

        def get_initial_queryset(self):
            return super().get_initial_queryset().filter(
                company=self.request.user.company
            )


WebixCreateView and WebixUpdateView
------------------------------------

Views for creating and updating model instances with support for inline formsets.

WebixCreateUpdateMixin
~~~~~~~~~~~~~~~~~~~~~~

Both ``WebixCreateView`` and ``WebixUpdateView`` share attributes from ``WebixCreateUpdateMixin``:

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Attribute
     - Default
     - Description
   * - ``logs_enable``
     - ``True``
     - Log create/update actions to Django's admin LogEntry
   * - ``errors_on_popup``
     - ``False``
     - Show validation errors in a popup window instead of inline
   * - ``enable_button_save_continue``
     - ``True``
     - Show "Save and Continue Editing" button
   * - ``enable_button_save_addanother``
     - ``True``
     - Show "Save and Add Another" button
   * - ``enable_button_save_gotolist``
     - ``True``
     - Show "Save and Go to List" button
   * - ``enable_button_reload``
     - ``True``
     - Show "Reload" button
   * - ``template_style``
     - ``None``
     - Form layout style: ``'standard'``, ``'tabs'``, or ``'monotabs'``
   * - ``default_id_tabbar``
     - ``None``
     - Default active tab ID when using tab layout

WebixCreateView
~~~~~~~~~~~~~~~

.. code-block:: python

    from django_webix.views import WebixCreateView
    from myapp.forms import ProductForm
    from myapp.models import Product

    class ProductCreateView(WebixCreateView):
        model = Product
        form_class = ProductForm

**Extra attributes:**

- ``model_copy_fields`` - List of field names to copy when duplicating (via ``?pk_copy=<pk>``).
  Defaults to all form fields if ``None``.
- ``inlines_copy_fields`` - Dict mapping inline classes to their copy fields.
- ``send_initial_data`` - Dict of initial data to pre-fill the form.

WebixUpdateView
~~~~~~~~~~~~~~~

.. code-block:: python

    from django_webix.views import WebixUpdateView
    from myapp.forms import ProductForm
    from myapp.models import Product

    class ProductUpdateView(WebixUpdateView):
        model = Product
        form_class = ProductForm

Lifecycle Hooks
~~~~~~~~~~~~~~~

Both create and update views provide hooks for custom business logic:

.. code-block:: python

    class ProductCreateView(WebixCreateView):
        model = Product
        form_class = ProductForm
        inlines = [ComponentInline]

        def pre_forms_valid(self, form=None, inlines=None, **kwargs):
            """Called before any data is saved. Use for validation or setup."""
            pass

        def post_form_save(self, form=None, inlines=None, **kwargs):
            """Called after the main form is saved but before inlines are saved."""
            # Example: set a computed field
            self.object.total = self.object.compute_total()
            self.object.save(update_fields=['total'])

        def post_forms_valid(self, form=None, inlines=None, **kwargs):
            """Called after all data (form + inlines) is saved."""
            # Example: send notification
            notify_team(self.object)

**Passing extra kwargs to the form:**

.. code-block:: python

    class ProductUpdateView(WebixUpdateView):
        model = Product
        form_class = ProductForm

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['company'] = self.request.user.company
            return kwargs

**Complete create/update example with inlines:**

.. code-block:: python

    from django_webix.views import WebixCreateView, WebixUpdateView
    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from myapp.forms import OrderForm, OrderItemForm
    from myapp.models import Order, OrderItem

    class OrderItemInline(WebixTabularInlineFormSet):
        model = OrderItem
        form_class = OrderItemForm
        factory_kwargs = {'extra': 1}

    class OrderCreateView(WebixCreateView):
        model = Order
        form_class = OrderForm
        inlines = [OrderItemInline]
        enable_button_save_addanother = False
        template_style = 'standard'
        model_copy_fields = ['customer', 'payment_terms']

        def post_forms_valid(self, form=None, inlines=None, **kwargs):
            super().post_forms_valid(form=form, inlines=inlines, **kwargs)
            self.object.recalculate_totals()

    class OrderUpdateView(WebixUpdateView):
        model = Order
        form_class = OrderForm
        inlines = [OrderItemInline]
        template_style = 'standard'

        def post_forms_valid(self, form=None, inlines=None, **kwargs):
            super().post_forms_valid(form=form, inlines=inlines, **kwargs)
            self.object.recalculate_totals()


WebixDeleteView
---------------

View for deleting a model instance. Shows related objects and protected relations before confirming.

.. code-block:: python

    from django_webix.views import WebixDeleteView
    from myapp.models import Product

    class ProductDeleteView(WebixDeleteView):
        model = Product

**Attributes:**

- ``logs_enable`` (default ``True``) - Log deletion to admin LogEntry
- ``exclude_models`` (default ``None``) - List of models to exclude from related objects display
- ``only_models`` (default ``None``) - Only show these models in related objects display

**Lifecycle hooks:**

.. code-block:: python

    class ProductDeleteView(WebixDeleteView):
        model = Product

        def pre_delete_valid(self, **kwargs):
            """Called before the object is deleted."""
            # Example: archive instead of delete
            super().pre_delete_valid(**kwargs)

        def post_delete_valid(self, **kwargs):
            """Called after the object is deleted. self.copied_object has the deleted data."""
            super().post_delete_valid(**kwargs)
            clear_product_cache(self.copied_object.pk)

        def get_failure_delete_related_objects(self, request, obj=None):
            """Return a list of strings describing why deletion is blocked."""
            errors = super().get_failure_delete_related_objects(request, obj)
            if obj and obj.invoiceitem_set.exists():
                errors.append('Cannot delete: product is referenced in invoices.')
            return errors


Inline Formsets
---------------

Inline formsets allow editing related models within a create/update view.

WebixTabularInlineFormSet
~~~~~~~~~~~~~~~~~~~~~~~~~

Renders the inline as a compact table (datatable):

.. code-block:: python

    from django_webix.formsets import WebixTabularInlineFormSet
    from myapp.models import OrderItem

    class OrderItemInline(WebixTabularInlineFormSet):
        model = OrderItem
        fields = '__all__'
        factory_kwargs = {
            'extra': 1,     # number of empty forms
            'min_num': 0,   # minimum required forms
        }

WebixStackedInlineFormSet
~~~~~~~~~~~~~~~~~~~~~~~~~

Renders each inline form in a stacked (full-width) layout:

.. code-block:: python

    from django_webix.formsets import WebixStackedInlineFormSet
    from myapp.forms import AddressForm
    from myapp.models import Address

    class AddressInline(WebixStackedInlineFormSet):
        model = Address
        form_class = AddressForm

**Inline attributes:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``model``
     - The related model
   * - ``form_class``
     - Custom form class (defaults to ``WebixModelForm``)
   * - ``fields``
     - Fields to include (alternative to ``form_class``)
   * - ``factory_kwargs``
     - Dict with ``extra``, ``min_num``, ``max_num``, ``fk_name``, etc.
   * - ``formset_kwargs``
     - Extra kwargs passed to the formset constructor
   * - ``container_id``
     - Custom DOM container ID for the inline
   * - ``auto_position``
     - Auto-position the inline (default ``True``)
   * - ``accordion_collapsed``
     - Start collapsed (default ``False``)
   * - ``name``
     - Display name for the inline section

Custom Formset Class
~~~~~~~~~~~~~~~~~~~~

For advanced validation or queryset filtering, provide a custom formset class:

.. code-block:: python

    from django_webix.formsets import BaseWebixInlineFormSet

    class ValidatedItemFormSet(BaseWebixInlineFormSet):

        def clean(self):
            super().clean()
            total = sum(
                form.cleaned_data.get('quantity', 0)
                for form in self.forms
                if not form.cleaned_data.get('DELETE', False)
            )
            if total <= 0:
                raise ValidationError('At least one item with quantity > 0 is required.')

    class OrderItemInline(WebixTabularInlineFormSet):
        model = OrderItem
        form_class = OrderItemForm
        custom_formset_class = ValidatedItemFormSet

**Custom queryset for inline:**

.. code-block:: python

    class ActiveItemInline(WebixStackedInlineFormSet):
        model = OrderItem
        fields = '__all__'

        def get_queryset(self):
            return self.inline_model.objects.filter(active=True)

**Multiple inlines in a single view:**

.. code-block:: python

    class OrderCreateView(WebixCreateView):
        model = Order
        form_class = OrderForm
        inlines = [OrderItemInline, OrderNoteInline, OrderAttachmentInline]
        template_style = 'tabs'


Permissions
-----------

WebixPermissionsMixin
~~~~~~~~~~~~~~~~~~~~~

All views inherit ``WebixPermissionsMixin`` which provides Django's standard permission checks.

**Permission attributes (set as class attributes to override):**

.. code-block:: python

    class RestrictedListView(WebixListView):
        model = Product
        add_permission = False        # Override: disable add for everyone
        change_permission = None      # None = use Django's standard check
        delete_permission = None
        view_permission = None
        check_permissions = True      # Set to False to skip all checks
        remove_disabled_buttons = False  # True = hide buttons instead of disabling

**Overriding permission methods:**

.. code-block:: python

    class TeamProductListView(WebixListView):
        model = Product

        def has_add_permission(self, request):
            return request.user.groups.filter(name='Editors').exists()

        def has_change_permission(self, request, obj=None):
            if obj and obj.locked:
                return False
            return super().has_change_permission(request, obj)

        def has_delete_permission(self, request, obj=None):
            return request.user.is_superuser

        def has_view_permission(self, request, obj=None):
            return True  # Everyone can view

**Custom permission messages:**

.. code-block:: python

    class ProductUpdateView(WebixUpdateView):
        model = Product
        form_class = ProductForm

        def get_info_no_change_permission(self, has_permission, request, obj=None):
            if not has_permission:
                if obj and obj.locked:
                    return ['This product is locked and cannot be edited.']
                return ['You do not have permission to edit this product.']
            return []

**Failure related objects (blocking operations):**

.. code-block:: python

    class ProductDeleteView(WebixDeleteView):
        model = Product

        def get_failure_delete_related_objects(self, request, obj=None):
            """Return list of error strings to block deletion."""
            errors = super().get_failure_delete_related_objects(request, obj)
            if obj and obj.order_items.exists():
                errors.append('Cannot delete: product has associated orders.')
            return errors

        def get_failure_add_blocking_objects(self, request):
            """Return list of dicts with 'text' and 'url' to block creation."""
            if not Category.objects.exists():
                return [{'text': 'Create a category first', 'url': reverse('myapp.category.create')}]
            return []


Signals
-------

django-webix dispatches signals during create, update, and delete operations:

.. code-block:: python

    from django_webix.views.generic.signals import (
        django_webix_view_pre_save,
        django_webix_view_pre_inline_save,
        django_webix_view_post_save,
        django_webix_view_pre_delete,
        django_webix_view_post_delete,
    )

**Signal arguments:**

- ``django_webix_view_pre_save`` - ``sender``, ``instance``, ``created`` (bool), ``form``, ``inlines``
- ``django_webix_view_pre_inline_save`` - ``sender``, ``instance``, ``created``, ``form``, ``inlines``
- ``django_webix_view_post_save`` - ``sender``, ``instance``, ``created``, ``form``, ``inlines``
- ``django_webix_view_pre_delete`` - ``sender``, ``instance``
- ``django_webix_view_post_delete`` - ``sender``, ``instance``

**Example receiver:**

.. code-block:: python

    from django.dispatch import receiver
    from django_webix.views.generic.signals import django_webix_view_post_save
    from myapp.models import Product

    @receiver(django_webix_view_post_save)
    def on_product_saved(sender, instance, created, form, inlines, **kwargs):
        if isinstance(instance, Product):
            if created:
                send_new_product_notification(instance)
            else:
                update_search_index(instance)


Decorators
----------

``@script_login_required``
~~~~~~~~~~~~~~~~~~~~~~~~~~

A Webix-aware login decorator that redirects to the login page via a JavaScript response
(instead of a standard HTTP redirect), ensuring proper behavior within the Webix SPA shell.

.. code-block:: python

    from django.utils.decorators import method_decorator
    from django_webix.utils.decorators import script_login_required

    @method_decorator(script_login_required, name='dispatch')
    class ProductListView(WebixListView):
        model = Product

This is the recommended way to protect views in django-webix, instead of Django's standard
``login_required`` decorator.
