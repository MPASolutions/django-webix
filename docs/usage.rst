Quick Start
===========

Install
-------

``django-webix`` is available on :samp:`https://pypi.python.org/pypi/django-webix/` install it simply with:

.. code-block:: bash

    $ pip install django-webix

Configure
---------

Settings
~~~~~~~~

Add ``django_webix`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_webix',
        # ...
    ]

Add ``django-webix`` URLconf to your project ``urls.py`` file

.. code-block:: python

    from django.conf.urls import url, include

    urlpatterns = [
        # ...
        url(r'^django-webix/', include('django_webix.urls')),
        # ...
    ]

Add internationalization to `TEMPLATES`

.. code-block:: python

    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                'context_processors': [
                    # ...
                    'django.template.context_processors.i18n',
                ],
            },
        },
    ]

Include ``webix static files`` folder in your django staticfiles folder as ``webix`` and add static configuration

.. code-block:: python

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'staticfiles'),
    )
    STATIC_URL = '/static/'


Usage
-----

Models
~~~~~~

Create the models (e.g. <app_name>/models.py)

.. code-block:: python

    from django.db import models

    from django_webix.models import GenericModelWebix


    class MyModel(GenericModelWebix):
        field = models.CharField(max_length=255)

        class WebixMeta:
            url_list = 'mymodel_list'
            url_create = 'mymodel_create'
            url_update = 'mymodel_update'
            url_delete = 'mymodel_delete'


    class InlineModel(models.Model):
        inline_field = models.CharField(max_length=255)
        my_model = models.ForeignKey(MyModel)


Forms
~~~~~

Create the forms (e.g. <app_name>/forms.py)

.. code-block:: python

    from django_webix.forms import WebixModelForm

    from <app_name>.models import MyModel

    class MyModelForm(WebixModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'


Views
~~~~~

Create the views (e.g. <app_name>/views.py)

.. code-block:: python


    import json

    from django.views.generic import TemplateView

    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from django_webix.views import WebixCreateWithInlinesView, WebixUpdateWithInlinesView, WebixDeleteView

    from <app_name>.forms import MyModelForm
    from <app_name>.models import MyModel, InlineModel


    class HomeView(TemplateView):
        template_name = 'base.html'


    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'


    class MyModelListView(TemplateView):
        template_name = 'list.js'

        def get_context_data(self, **kwargs):
            context = super(MyModelListView, self).get_context_data(**kwargs)
            context['datalist'] = json.dumps([{
                'id': i.pk,
                'field': i.field
            } for i in MyModel.objects.all()])
            return context


    class MyModelCreateView(WebixCreateWithInlinesView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm


    class MyModelUpdateView(WebixUpdateWithInlinesView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm


    class MyModelDeleteView(WebixDeleteView):
        model = MyModel


Urls
~~~~

Register the views url (e.g. <project_name>/urls.py)

.. code-block:: python

    from django.conf.urls import url

    from <app_name>.views import HomeView, MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView

    urlpatterns = [
        # ...
        url(r'^$', HomeView.as_view(), name='home'),

        url(r'^mymodel/list$', MyModelListView.as_view(), name='mymodel_list'),
        url(r'^mymodel/create$', MyModelCreateView.as_view(), name='mymodel_create'),
        url(r'^mymodel/update/(?P<pk>\d+)$', MyModelUpdateView.as_view(), name='mymodel_update'),
        url(r'^mymodel/delete/(?P<pk>\d+)$', MyModelDeleteView.as_view(), name='mymodel_delete'),
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

            load_js('{% url 'mymodel_list' %}');
        });
    </script>
    </html>


List sample
~~~~~~~~~~~

A sample of MyModel list written with webix library (e.g. <app_name>/templates/list.js)

.. code-block:: javascript

    webix.ui([], $$("{{ view.webix_view_id|default:"content_right" }}"));

    $$("{{ view.webix_view_id|default:"content_right" }}").addView({
        rows: [
            {
                id: '{{ object_list.model.get_model_name }}',
                view: "datatable",
                resizeColumn: true,
                data: {{ datalist|safe }},
                select: "row",
                columns: [
                    {
                        id: "field",
                        header: "Field",
                        fillspace: true
                    }
                ],
                on: {
                    onItemDblClick: function (id, e, trg) {
                        var $this = this;

                        $.ajax({
                            url: '{% url 'mymodel_update' 1 %}'.replace('1', id.row),
                            dataType: "script",
                            success: function (text, data, XmlHttpRequest) {
                            },
                            error: function () {
                                alert('Error')
                            }
                        });
                    }
                }
            },
            {
                view: "toolbar",
                id: "myToolbar",
                cols: [
                    {
                        view: "button", value: "New", width: 100, align: "center", click: function () {
                            $.ajax({
                                url: '{% url 'mymodel_create' %}',
                                dataType: "script",
                                success: function (text, data, XmlHttpRequest) {
                                },
                                error: function () {
                                    alert('Error')
                                }
                            });
                        }
                    }
                ]
            }
        ]
    }, -1);

