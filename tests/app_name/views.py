#!/usr/bin/env python

import json

from django.views.generic import TemplateView, FormView

from django_webix.views import (WebixCreateView,
                                WebixUpdateView,
                                WebixDeleteView, WebixListView)
from .forms import (MyLoginForm,
                    InlineStackedModelInline,
                    InlineModelInline,
                    InlineEmptyModelInline,
                    MyModelForm)
from .models import (MyModel,
                     InlineModel,
                     InlineStackedModel)

####################### FORMVIEW #######################

class MyLoginView(FormView):
    form_class = MyLoginForm
    template_name = 'django_webix/generic/create.js'

####################### LISTVIEW #######################

class MyModelListView(TemplateView):
    template_name = 'list.js'

    def get_context_data(self, **kwargs):
        context = super(MyModelListView, self).get_context_data(**kwargs)
        context['datalist'] = json.dumps([{
            'id': i.pk,
            'field': i.field
        } for i in MyModel.objects.all()])
        return context

####################### CREATEVIEW #######################

class MyModelCreateBaseView(WebixCreateView):
    model = MyModel
    form_class = MyModelForm


class MyModelCreateView(WebixCreateView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    permissions = False


class MyModelCreateErrorView(WebixCreateView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    style = 'error'

    url_create = 'app_name.mymodel.create_error'

####################### UPDATEVIEW #######################

class MyModelUpdateBaseView(WebixUpdateView):
    model = MyModel
    form_class = MyModelForm

class MyModelUpdateView(WebixUpdateView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm


class MyModelUpdateErrorView(WebixUpdateView):
    model = MyModel
    inlines = [InlineModelInline, InlineStackedModelInline, InlineEmptyModelInline]
    form_class = MyModelForm
    style = 'error'

    url_create = 'app_name.mymodel.update_error'

####################### DELETEVIEW #######################

class MyModelDeleteBaseView(WebixDeleteView):
    model = MyModel

class MyModelDeleteView(WebixDeleteView):
    model = MyModel

####################### LISTVIEW #######################

class MyModelListBaseView(WebixListView):
    model = MyModel

####################### EXTRA TO CHECK #######################
#class InlineModelUpdateView(WebixUpdateView):
#    model = InlineModel
#    fields = '__all__'


#class InlineStackedModelDelete(WebixDeleteView):
#    model = InlineStackedModel
