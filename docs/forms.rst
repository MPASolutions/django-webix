Forms
=====

Form
~~~~

Create the forms (e.g. <app_name>/forms.py)

.. code-block:: python

    from django_webix.forms import WebixForm, WebixModelForm

    class CustomForm(WebixForm):
        # field1...
        class Meta:
            localized_fields = ('__all__') # to use comma as separator in i18n

    from <app_name>.models import MyModel

    class MyModelForm(WebixModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            localized_fields = ('__all__') # to use comma as separator in i18n

How to customization parameters of Form/ModelForm (extra from django standard form)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    form_fix_height = None

Used for fix form height and enable scroller when is too height.

.. code-block:: python

    form_fix_height = None

Used for fix form height and enable scroller when is too height.

.. code-block:: python

    min_count_suggest = 100

Used for ModelMultipleChoiceField and ModelChoiceField fields to set him from dropdown to autocomplete field.

.. code-block:: python

    style = 'stacked' # 'tabular'

Used as style when this form is used to create an Inline.

.. code-block:: python

    label_width = 300

Used as width for label of field.

.. code-block:: python

    label_align = 'left' # center ; rigth

Used as align for label of field.

How to customization rendering of Form/ModelForm (used from as_webix)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

get_elements
____________

.. code-block:: python

    @property/ModelForm
    def get_elements(self):

For each field get_elements convert standard django field to a webix-field configuration (each field is a flat keys-values dict).
Extra: Only GeoField, FileField and ImageField are created as more complex strucure.
Example of override it:

.. code-block:: python

    @property
    def get_elements(self):
        elements = super().get_elements
        elements[self.add_prefix('field_name')].update({
            'readonly': 'readonly',
            'disabled': True,
            'type': 'password',
            'width': 300,
            'labelWidth': 150,
            'label': _('field name text new'),
            'placeholder': _("Search..."),
            'value': 5,
            'css': "multiline"
            ''
            })
        return elements

get_fieldsets
_____________

.. code-block:: python

    def get_fieldsets(self, fs=None):
        self.readonly_fields = [] # automatically popupated, but is possibile to add some fields
        self.autocomplete_fields = [] # automatically popupated with ModelMultipleChoiceField and ModelChoiceField, but is possibile to add some fields
        self.autocomplete_fields_exclude = [] # automatically popupated with ModelMultipleChoiceField and ModelChoiceField, but is possibile to add some fields
        if fs is None: fs = self.get_elements
        # create an output structure
        # otherwise can have flat structure with a field for each rows like django standard
        return super().get_fieldsets(fs=fs)

If you want to change not only field by field but as form will be rendered you can work on get_fieldsets.
Example of override it:

.. code-block:: python

    def get_fieldsets(self, fs=None):
        self.autocomplete_fields_exclude = ['field_1']
        self.autocomplete_fields = ['field_2']
        if fs is None: fs = self.get_elements
        # like override function get_elements here is possibile to force webix-field-dict
        return [
            {'cols': [fs['field_1', {}]]},
            {'cols': [fs['field_2'], fs['field_3']]},
            {'template': "section webix example", 'type': "section"},
            {'cols': [fs['field_4'], {} ]},
        ]

Permissions and request
~~~~~~~~~~~~~~~~~~~~~~~

Into __init__ function of form set are set request and permissions that are used into get_fieldsets or get_elements to custumization pourposes.

.. code-block:: python

        self.request
        self.has_add_permission
        self.has_change_permission
        self.has_delete_permission
