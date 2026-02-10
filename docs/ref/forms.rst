Forms
=====

django-webix provides ``WebixForm`` and ``WebixModelForm`` classes that extend Django's standard forms
to generate `Webix <https://webix.com>`_ UI-compatible field structures. They convert standard Django
fields into Webix widget configurations (datepicker, richselect, combo, multicombo, etc.) and support
layouts with rows, cols, sections, and tabs.

.. code-block:: python

    from django_webix.forms import WebixForm, WebixModelForm


WebixForm
---------

A non-model form for custom forms that do not map directly to a Django model.

.. code-block:: python

    from django import forms
    from django_webix.forms import WebixForm

    class ContactForm(WebixForm):
        name = forms.CharField(max_length=100)
        email = forms.EmailField()
        message = forms.CharField(widget=forms.Textarea)

        class Meta:
            localized_fields = '__all__'

**Example with dynamic choices and extra kwargs:**

.. code-block:: python

    class OperatorFilterForm(WebixForm):
        operator = forms.ModelChoiceField(queryset=Operator.objects.none())
        date_from = forms.DateField(required=False)
        date_to = forms.DateField(required=False)

        class Meta:
            localized_fields = '__all__'

        def __init__(self, *args, **kwargs):
            queryset = kwargs.pop('queryset', None)
            super().__init__(*args, **kwargs)
            if queryset is not None:
                self.fields['operator'].queryset = queryset


WebixModelForm
--------------

A model-bound form that maps fields to a Django model, automatically generating Webix widgets based
on the model field types.

.. code-block:: python

    from django_webix.forms import WebixModelForm
    from myapp.models import Customer

    class CustomerForm(WebixModelForm):
        class Meta:
            model = Customer
            fields = '__all__'
            localized_fields = '__all__'

**Complete Meta options:**

.. code-block:: python

    class CustomerForm(WebixModelForm):
        class Meta:
            model = Customer
            fields = ['name', 'email', 'phone', 'address', 'category']
            # or: fields = '__all__'
            exclude = ['internal_notes']
            localized_fields = '__all__'  # use comma as decimal separator in i18n
            widgets = {
                'address': forms.Textarea(attrs={'rows': 3}),
            }
            labels = {
                'name': 'Full Name',
            }
            help_texts = {
                'email': 'Primary contact email address.',
            }


Form Parameters
---------------

These class-level attributes control the rendering behavior of the form. They are defined on
``BaseWebixMixin`` and apply to both ``WebixForm`` and ``WebixModelForm``.

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Parameter
     - Default
     - Description
   * - ``form_fix_height``
     - ``None``
     - Fix the form height (in px). When set, a vertical scroller is enabled if the form exceeds this height.
   * - ``min_count_suggest``
     - ``100``
     - Threshold for ``ModelChoiceField`` and ``ModelMultipleChoiceField``: if the queryset count exceeds
       this value, the field switches from a dropdown to an autocomplete (suggest) widget.
   * - ``style``
     - ``'stacked'``
     - Layout style. Use ``'stacked'`` for standard form layout or ``'tabular'`` when the form is
       rendered as an inline in tabular mode.
   * - ``label_width``
     - ``300``
     - Width in pixels of the label for each field.
   * - ``label_width_mobile``
     - ``120``
     - Width in pixels of the label on mobile devices (requires ``django-user-agents``).
   * - ``suggest_width``
     - ``None``
     - Width of the suggest/autocomplete dropdown. ``None`` means it inherits the parent width.
       Set to an ``int`` value to specify a fixed width.
   * - ``label_align``
     - ``'left'``
     - Alignment for field labels. Options: ``'left'``, ``'center'``, ``'right'``.
   * - ``autocomplete_fields``
     - ``[]``
     - List of field names that should use autocomplete (suggest) widgets. Automatically populated
       for ``ModelChoiceField`` and ``ModelMultipleChoiceField`` whose queryset exceeds
       ``min_count_suggest``.
   * - ``autocomplete_fields_exclude``
     - ``[]``
     - List of field names that should **never** use autocomplete, even if their queryset count
       exceeds ``min_count_suggest``.
   * - ``readonly_fields``
     - ``[]``
     - List of field names that should be rendered as read-only (disabled). Automatically set to
       all fields when the user lacks change permission.

**Example:**

.. code-block:: python

    class ProductForm(WebixModelForm):
        form_fix_height = 600
        min_count_suggest = 50
        label_width = 250
        label_align = 'left'

        class Meta:
            model = Product
            fields = '__all__'
            localized_fields = '__all__'


``get_elements``
----------------

The ``get_elements`` property returns an ``OrderedDict`` where each key is a prefixed field name
and each value is a dictionary describing the Webix widget configuration. Override it to customize
individual fields.

.. code-block:: python

    @property
    def get_elements(self):
        elements = super().get_elements

        # Make a field readonly and disabled
        elements[self.add_prefix('serial_number')].update({
            'readonly': 'readonly',
            'disabled': True,
        })

        # Set custom width and label
        elements[self.add_prefix('quantity')].update({
            'width': 200,
            'labelWidth': 100,
            'label': 'Qty',
        })

        # Add placeholder text
        elements[self.add_prefix('search_term')].update({
            'placeholder': 'Search...',
        })

        # Hide a field (renders hidden input)
        elements[self.add_prefix('internal_code')].update({
            'hidden': True,
        })

        # Add custom CSS class
        elements[self.add_prefix('description')].update({
            'css': 'multiline',
        })

        # Set input alignment
        elements[self.add_prefix('amount')].update({
            'inputAlign': 'right',
        })

        return elements

**Key:** Always use ``self.add_prefix('field_name')`` to reference fields. This ensures correct
behavior when the form is used as an inline (where each form gets a unique prefix like
``inlinemodel_set-0-field_name``).


``get_fieldsets``
-----------------

Override ``get_fieldsets`` to control the layout of the form. By default, all fields are rendered
one per row. You can organize fields into rows (``cols``), sections, and tabs.

**Basic rows/cols layout:**

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        return [
            {'cols': [fs[self.add_prefix('first_name')], fs[self.add_prefix('last_name')]]},
            {'cols': [fs[self.add_prefix('email')], {}]},
            {'cols': [fs[self.add_prefix('phone')], fs[self.add_prefix('mobile')]]},
        ]

**Section headers:**

Use ``"type": "section"`` for a bold section divider or ``"type": "header"`` for a smaller header:

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        return [
            {'template': 'Personal Information', 'type': 'section'},
            {'cols': [fs[self.add_prefix('first_name')], fs[self.add_prefix('last_name')]]},
            {'cols': [fs[self.add_prefix('birth_date')], {}]},

            {'template': 'Contact Details', 'type': 'section'},
            {'cols': [fs[self.add_prefix('email')], fs[self.add_prefix('phone')]]},
        ]

**Tab layout with tabbar + multiview:**

For complex forms, use the tab layout (requires ``template_style = 'tabs'`` on the view):

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        return [
            {'view': 'tabbar', 'id': 'main_tabbar', 'multiview': True, 'value': 'general_tab',
             'options': [
                 {'id': 'general_tab', 'value': 'General'},
                 {'id': 'details_tab', 'value': 'Details'},
             ]},
            {'cells': [
                {'id': 'general_tab', 'rows': [
                    {'cols': [fs[self.add_prefix('name')], fs[self.add_prefix('code')]]},
                    {'cols': [fs[self.add_prefix('category')], {}]},
                ]},
                {'id': 'details_tab', 'rows': [
                    {'cols': [fs[self.add_prefix('description')]]},
                    {'cols': [fs[self.add_prefix('notes')]]},
                ]},
            ]},
        ]

**Setting autocomplete_fields and readonly_fields in get_fieldsets:**

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        self.autocomplete_fields_exclude = ['category']
        self.autocomplete_fields = ['supplier']
        fs = self.get_elements
        return [
            {'cols': [fs[self.add_prefix('name')], fs[self.add_prefix('category')]]},
            {'cols': [fs[self.add_prefix('supplier')], {}]},
        ]

**Conditional field visibility based on instance state:**

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        rows = [
            {'cols': [fs[self.add_prefix('name')], fs[self.add_prefix('status')]]},
        ]
        # Show approval fields only for existing records
        if hasattr(self, 'instance') and self.instance.pk is not None:
            rows.append(
                {'cols': [fs[self.add_prefix('approved_by')], fs[self.add_prefix('approved_date')]]}
            )
        return rows


``get_tabular_fields_header``
-----------------------------

When a form is used as a tabular inline, ``get_tabular_fields_header`` generates the column headers
for the datatable. Override it to customize header text, widths, or add sorting.

.. code-block:: python

    @property
    def get_tabular_fields_header(self):
        headers = super().get_tabular_fields_header
        # Customize a column width
        if self.add_prefix('quantity') in headers:
            headers[self.add_prefix('quantity')].update({'width': 100})
        return headers


Form Validation
---------------

**Standard clean methods:**

Use Django's standard ``clean_<fieldname>()`` and ``clean()`` methods:

.. code-block:: python

    class CustomerForm(WebixModelForm):
        class Meta:
            model = Customer
            fields = '__all__'

        def clean_email(self):
            email = self.cleaned_data.get('email')
            if email and not email.endswith('@example.com'):
                raise forms.ValidationError('Only @example.com emails are allowed.')
            return email

        def clean(self):
            cleaned_data = super().clean()
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')
            if start_date and end_date and start_date > end_date:
                raise forms.ValidationError('Start date must be before end date.')
            return cleaned_data

**Warnings with ``warnings_clean``:**

django-webix supports non-blocking warnings that are shown to the user before saving. The user can
choose to proceed or cancel. Define a ``warnings_clean()`` method that returns a list of tuples
``(field_name, message)``:

.. code-block:: python

    class OrderForm(WebixModelForm):
        class Meta:
            model = Order
            fields = '__all__'

        def warnings_clean(self):
            warnings = []
            if self.cleaned_data.get('quantity', 0) > 1000:
                warnings.append(('quantity', 'Large quantity: are you sure?'))
            return warnings

The view must have ``has_warning_clean`` returning ``True`` (detected automatically if the form
class defines ``warnings_clean``). When warnings are present, the user sees a confirmation dialog
before the save proceeds.


Permissions and Request
-----------------------

The form's ``__init__`` receives the ``request`` object and permission flags from the view.
These are available inside ``get_elements`` and ``get_fieldsets`` for conditional rendering:

.. code-block:: python

    # Available in form methods:
    self.request                 # The current HttpRequest
    self.has_add_permission      # bool - user can add
    self.has_change_permission   # bool - user can change
    self.has_delete_permission   # bool - user can delete
    self.parent_model            # The parent model (for inlines)

**Example: conditionally hiding a field based on permissions:**

.. code-block:: python

    @property
    def get_elements(self):
        elements = super().get_elements
        if not self.has_change_permission:
            # The base mixin already makes all fields readonly when
            # has_change_permission is False, but you can add extra logic:
            elements[self.add_prefix('price')].update({'hidden': True})
        return elements

**Example: using request in get_fieldsets:**

.. code-block:: python

    def get_fieldsets(self, **kwargs):
        fs = self.get_elements
        rows = [
            {'cols': [fs[self.add_prefix('name')], fs[self.add_prefix('code')]]},
        ]
        if self.request and self.request.user.is_superuser:
            rows.append({'cols': [fs[self.add_prefix('admin_notes')]]})
        return rows


Field Type Mapping
------------------

django-webix automatically maps Django field types to Webix widgets:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Django Field
     - Webix Widget
     - Notes
   * - ``CharField``
     - ``text`` / ``textarea``
     - ``textarea`` when ``widget=Textarea``
   * - ``EmailField``
     - ``text``
     -
   * - ``IntegerField``
     - ``text``
     - With ``isInteger`` validation rule
   * - ``FloatField`` / ``DecimalField``
     - ``text``
     - With ``isNumber`` validation, localized formatting
   * - ``DateField``
     - ``datepicker``
     - Format: ``%d/%m/%Y``
   * - ``DateTimeField``
     - ``datepicker``
     - With ``timepicker: True``
   * - ``TimeField``
     - ``datepicker``
     - Type: ``time``
   * - ``BooleanField``
     - ``checkbox``
     -
   * - ``ChoiceField``
     - ``richselect``
     -
   * - ``ModelChoiceField``
     - ``richselect`` / ``combo``
     - ``combo`` when count > 6. Switches to autocomplete when count > ``min_count_suggest``
   * - ``ModelMultipleChoiceField``
     - ``multicombo``
     - Requires PRO Webix license. Auto-suggest when count > ``min_count_suggest``
   * - ``FileField``
     - ``uploader``
     - With download/delete buttons
   * - ``ImageField``
     - ``uploader``
     - With image preview
   * - ``GeometryField``
     - ``textarea`` (hidden)
     - With map integration when ``django_webix_leaflet`` is installed
   * - ``JSONField``
     - ``text`` / ``textarea``
     - PostgreSQL only
   * - ``URLField`` / ``SlugField``
     - ``text``
     -
   * - Widget ``RadioSelect``
     - ``radio``
     - Overrides the default widget
   * - Widget ``PasswordInput``
     - ``search`` with eye icon
     -
   * - Widget ``HiddenInput``
     - hidden field
     -
