Views
=====

WebixTemplateView (used for webix rendering)
--------------------------------------------

To use instead of TemplateView to can override these extra functions.

.. code-block:: python

    from django_webix.views import WebixTemplateView
    class CustomView(WebixTemplateView):
        template_name = 'base.html'

        qxs_layers # only for GIS support

        def get_container_id(self, request):
            return settings.WEBIX_CONTAINER_ID

        def get_overlay_container_id(self, request):
            return getattr(settings, 'WEBIX_OVERLAY_CONTAINER_ID', settings.WEBIX_CONTAINER_ID)

Base Template
~~~~~~~~~~~~~

Create a base html template (e.g. <app_name>/templates/base.html)

.. code-block:: html

    {% load i18n %}

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>

        {% include "django_webix/static_meta.html" %}
    </head>
    <body>
    </body>

    <script type="text/javascript" charset="utf-8">
        webix.ready(function () {
            webix.ui({
                id: 'content_right',
                rows: []
            });

            webix.extend($$('content_right'), webix.OverlayBox);

            load_js('{% url 'myapplication.mymodel.list' %}');
        });
    </script>
    </html>

WebixFormView
-------------

Custom View for manage WebixForm and WebixModelForm

.. code-block:: python

    from django_webix.utils.decorators import script_login_required
    from django_webix.views.generic.base import WebixFormView
    @method_decorator(script_login_required, name='dispatch')
    class AttrezzaturaMasterSlave(WebixFormView):
        form_class = CustomWebixForm


WebixListView
-------------

Mainly is based on a model and his queryset.

.. code-block:: python

    from django_webix.views import WebixListView
    from <app_name>.models import MyModel

    class MyModelListView(WebixListView):
        model = MyModel

        footer = True
        order_by = None
        actions = []  # [multiple_delete_action]

        # paging
        enable_json_loading = True
        paginate_count_default = 100
        paginate_start_default = 0
        paginate_count_key = 'count'
        paginate_start_key = 'start'

        # template vars
        template_name = 'django_webix/generic/list.js'
        title = None
        actions_style = None # ['buttons', 'select']
        enable_column_webgis = True
        enable_column_copy = True
        enable_column_delete = True
        enable_row_click = True
        type_row_click = 'single'  # or 'double'
        enable_actions = True


        def get_initial_queryset(self,):
            return super().get_initial_queryset()

        fields = [
            { # char example
                'field_name': 'XXX',
                'datalist_column': '''{id: "XXX", serverFilterType:"icontains", header: ["{{_("TEXT1")|escapejs}}", {content: "serverFilter"}], fillspace: true, sort: "server"}'''
            },
            { # FK example
                'field_name': 'YYYY',
                'datalist_column': ''' {id: "YYYY", serverFilterType:"exact", header: ["{{_("TEXT2")|escapejs}}", {content: "serverSelectFilter", options:YYYY_options}], adjust: "all", sort: "server"}'''
            },
            { # number example (in this case by interface is possibile to write for example "<=5" )
                'click_action': '''custom_js_function_to_add_into_js(el['id']);''',
                'field_name': 'ZZZZ',
                'footer': Sum('ZZZZ'),
                'datalist_column': '''{id: "ZZZZ", serverFilterType:"numbercompare", header: ["{{_("TEXT3")|escapejs}}", {content: "numberFilter"}], css: {'text-align': 'right'}, adjust: "all", sort: "server"}'''
            },
        ]

There some example for filtering:

- TextField ex. serverFilterType:"icontains"  {content: "serverFilter"}

- FloatField ex. serverFilterType:"numbercompare"  {content: "numberFilter"}

- ForeignKey ex. serverFilterType:"exact" {content: "serverSelectFilter" options:YYYY_options}

- DateField ex. serverFilterType:"range" {content: "serverDateRangeFilter"}

- BooleanField ex. use template:custom_checkbox_yesnonone and add {content: "serverSelectFilter" , options:[{id: 'True', value: 'Yes'}, {id: 'False', value: 'No'}] }


WebixCreateView and WebixUpdateView
-----------------------------------

WebixCreateUpdateMixin
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class WebixCreateUpdateMixin:
        logs_enable = True
        errors_on_popup = False
        enable_button_save_continue = True
        enable_button_save_addanother = True
        enable_button_save_gotolist = True
        template_style = 'standard' # ['standard', 'tabs', 'monotabs']


Inlines
~~~~~~~

.. code-block:: python

    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from <app_name>.models import InlineModel

    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'

        def get_queryset(self): # eventually override
            return self.inline_model.objects.filter(**filters)

Custom formset for Inlines
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django_webix.formsets import BaseWebixInlineFormSet

    class CustomInlineFormSet(BaseWebixInlineFormSet):
        # ...

    class InlineModelInline(WebixStackedInlineFormSet):
        # ...
        custom_formset_class = CustomInlineFormSet
        # ...

WebixCreateView and WebixUpdateView
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from django_webix.views import WebixListView, WebixCreateView, WebixUpdateView, WebixDeleteView

    from <app_name>.forms import MyModelForm
    from <app_name>.models import MyModel, InlineModel

    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'

    class MyModelCreateView(WebixCreateView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm
        model_copy_fields = []

    def pre_forms_valid(self, form=None, inlines=None, **kwargs):
        '''
        Before all data saving
        '''
    def post_form_save(self, form=None, inlines=None, **kwargs):
        '''
        After form save and before inlines save
        '''
    def post_forms_valid(self, form=None, inlines=None, **kwargs):
        '''
        After all data saved
        '''

CreateView and UpdateView Signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When createview and updateview work some signals are sended.

.. code-block:: python

    django_webix_view_pre_save.send(sender=self,
                    instance=None,
                    created=True,
                    form=form,
                    inlines=inlines)
    django_webix_view_pre_inline_save.send(sender=self,
                       instance=self.object,
                       created=True,
                       form=form,
                       inlines=inlines)
    django_webix_view_post_save.send(sender=self,
                    instance=self.object,
                    created=True,
                    form=form,
                    inlines=inlines)

WebixDeleteView
---------------

.. code-block:: python

    class MyModelDeleteView(WebixDeleteView):
        model = MyModel

        def pre_delete_valid(self):
            pass

        def post_delete_valid(self):
            pass

        def get_failure_delete_related_objects(self, request, obj=None):
            return []



DeleteView Signals
~~~~~~~~~~~~~~~~~~

When deleteview works some signals are sended.

.. code-block:: python

    django_webix_view_pre_delete.send(sender=self, instance=self.object)
    django_webix_view_post_delete.send(sender=self, instance=self.copied_object)
