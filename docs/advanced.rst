Advanced Usage
==============

Inline Templates
----------------

.. code-block:: python

    from django_webix.formsets import WebixTabularInlineFormSet, WebixStackedInlineFormSet
    from django_webix.views import WebixCreateWithInlinesUnmergedView, WebixUpdateWithInlinesUnmergedView

    from <app_name>.forms import MyModelForm
    from <app_name>.models import MyModel, InlineModel


    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'


    class MyModelCreateView(WebixCreateWithInlinesUnmergedView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm


    class MyModelUpdateView(WebixUpdateWithInlinesUnmergedView):
        model = MyModel
        inlines = [InlineModelInline]
        form_class = MyModelForm


Inline QuerySet
---------------

.. code-block:: python

    from django_webix.formsets import WebixStackedInlineFormSet
    from django_webix.views import WebixCreateWithInlinesView, WebixUpdateWithInlinesView, WebixDeleteView

    from <app_name>.models import InlineModel


    class InlineModelInline(WebixStackedInlineFormSet):
        model = InlineModel
        fields = '__all__'

        def get_queryset(self):
            return self.inline_model.objects.filter(**filters)


Custom FormSet Class
--------------------

.. code-block:: python

    from django_webix.formsets import BaseWebixInlineFormSet


    class CustomInlineFormSet(BaseWebixInlineFormSet):
        # ...


    class InlineModelInline(WebixStackedInlineFormSet):
        # ...
        custom_formset_class = CustomInlineFormSet
        # ...
