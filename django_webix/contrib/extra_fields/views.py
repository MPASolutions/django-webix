from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator

from django_webix.views import WebixDetailView as DetailView
from django_webix.contrib.extra_fields.models import ModelField

@method_decorator(login_required, name='dispatch')
class ModelFieldConfigView(DetailView):
    model = ModelField
    template_name = 'blank.html'

    def get(self, request, *args, **kwargs):
        json_response = {
            'widget': self.object.field_type,
            'locked': self.object.locked,
            'options': list({'id': i['value'], 'value':i['key']} for i in self.object.modelfieldchoice_set.values('key', 'value')),
        }
        return JsonResponse(json_response, safe=False)
