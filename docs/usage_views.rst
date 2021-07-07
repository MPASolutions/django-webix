Views
=====

Usage
-----

ModelForm
~~~~~

Create the forms (e.g. <app_name>/forms.py)

.. code-block:: python

    from django_webix.forms import WebixModelForm

    from <app_name>.models import MyModel

    class MyModelForm(WebixModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            localized_fields = ('__all__')

GenericViews
~~~~~

Create the views (e.g. <app_name>/views.py)

.. code-block:: python

    import json

    from django.views.generic import TemplateView

    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from django_webix.views import WebixListView, WebixCreateView, WebixUpdateView, WebixDeleteView

    from <app_name>.forms import MyModelForm
    from <app_name>.models import MyModel, InlineModel


    class HomeView(TemplateView):
        template_name = 'base.html'


    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'


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

.. code-block:: python

    class MyModelCreateView(WebixCreateView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm

.. code-block:: python

    class MyModelUpdateView(WebixUpdateView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm

.. code-block:: python

    class MyModelDeleteView(WebixDeleteView):
        model = MyModel


CreateView and UpdateView Signals
~~~~~~~~~~~~~~~~

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

DeleteView Signals
~~~~~~~~~~~~~~~~

When deleteview works some signals are sended.

.. code-block:: python
        django_webix_view_pre_delete.send(sender=self, instance=self.object)
        django_webix_view_post_delete.send(sender=self, instance=self.copied_object)


ListView Actions
~~~~~~~~~~~~~~~~

Create the actions (e.g. <app_name>/actions.py)

.. code-block:: python


    from django.http import JsonResponse

    from django_webix.views.generic.decorators import action_config

    # list checkboxes actions
    @action_config(action_key='CUSTOMKEY',
                   response_type='json',
                   short_description='TEXT4')
    def my_action(self, request, qs):
        qs.update(status='p')
        return JsonResponse({
            "status": True,
            "message": 'Updated {} items'.format(qs.count()),
            "redirect_url": self.get_url_list(),
        }, safe=False)


Urls
~~~~

Register the views url (e.g. <project_name>/urls.py)

.. code-block:: python

    from django.urls import path

    from <app_name>.views import HomeView, MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView

    urlpatterns = [
        # ...
        path('', HomeView.as_view(), name='home'),

        path('mymodel/list', MyModelListView.as_view(), name='myapplication.mymodel.list'),
        path('mymodel/create', MyModelCreateView.as_view(), name='myapplication.mymodel.create'),
        path('mymodel/update/<int:pk>', MyModelUpdateView.as_view(), name='myapplication.mymodel.update'),
        path('mymodel/delete/<int:pk>', MyModelDeleteView.as_view(), name='myapplication.mymodel.delete'),
        # ...
    ]


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
