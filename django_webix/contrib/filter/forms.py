import json
from django.apps import apps
from django.conf import settings
from django_webix.forms import WebixModelForm
from django_webix.contrib.filter.models import WebixFilter
from django_webix.contrib.filter.utils.json_converter import get_JSON_for_JQB, get_JSON_from_DB
from django_webix.contrib.filter.utils.config import get_enabled_model
from django_webix.contrib.filter.utils.check import check_filter


class WebixFilterForm(WebixModelForm):
    class Meta:
        localized_fields = '__all__'
        model = WebixFilter
        fields = ['title', 'description', 'model', 'visibility', 'assignees_groups', 'shared_edit_group', 'filter']

    def __init__(self, *args, **kwargs):
        visibility_choices = kwargs.pop("visibility_choices", None)

        super().__init__(*args, **kwargs)

        # Set visibility
        if visibility_choices is not None:
            self.fields["visibility"].choices = \
                [i for i in self.fields["visibility"].choices if i[0] in visibility_choices]

        json_elaborated = self.initial.get('filter', None)
        initial_model = self.initial.get('model', None)

        if json_elaborated is not None and initial_model is not None:
            names = initial_model.split('.')
            try:
                model_class = apps.get_model(app_label=names[0], model_name=names[1])
                json_elaborated = get_JSON_from_DB(json_elaborated)
                self.json_elaborated = get_JSON_for_JQB(json_elaborated, model_class)
                if not check_filter(self.json_elaborated):
                    self.json_elaborated = None
            except Exception as e:
                if isinstance(json_elaborated, str):
                    try:
                        model_class = apps.get_model(app_label=names[0], model_name=names[1])
                        json_elaborated = json.loads(json_elaborated)
                        self.json_elaborated = get_JSON_for_JQB(json_elaborated, model_class)
                    except:
                        self.json_elaborated = None
                else:
                    self.json_elaborated = None
        else:
            self.json_elaborated = None

    def get_fieldsets(self, fs=None):
        if fs is None:
            fs = self.get_elements

        fs['filter'].update({'hidden': True})
        fs['description'].update({'height': 100, 'maxHeight': 100})
        fs['model'].update({
            'view': 'combo',
            'options': [{
                'id': "{}.{}".format(model._meta.app_label, model._meta.model_name),
                'value': "{} ({})".format(model._meta.verbose_name, model._meta.app_label)
            } for model in get_enabled_model(initial=True)]
        })

        # Set shared_edit_groups
        shared_edit_group_hidden = True
        if "shared_edit_groups" in settings.DJANGO_WEBIX_FILTER:
            # Check configuration of the first group found
            group = self.request.user.groups.filter(
                name__in=settings.DJANGO_WEBIX_FILTER["shared_edit_groups"].keys()
            ).first()
            if group is not None and (self.instance.pk is None or self.instance.insert_user == self.request.user):
                shared_edit_group_hidden = False

        if self.instance.pk:
            fs['model'].update({'readonly': 'readonly', 'disabled': True})

        return [{'rows': [
            {'cols': [fs['title']]},
            {'cols': [fs['model']]},
            {'cols': [fs['description']]},
            {'cols': [fs['visibility']], 'hidden': len(self.fields["visibility"].choices) <= 1},
            {'cols': [fs['assignees_groups']]},
            {'cols': [fs['shared_edit_group']], 'hidden': shared_edit_group_hidden},
            {'cols': [fs['filter'], {
                'id': 'json_loader_jqb',
                'view': 'textarea',
                'value': json.dumps(self.json_elaborated),
                'hidden': True,
            }], "hidden": True},
            {'cols': [
                {'view': 'scrollview', 'scroll': 'native-y', 'body': {'id': 'querybuilder-container', 'rows': []}}
            ], 'paddingY': 20},
        ]}]

    def clean(self):
        cleaned_data = super().clean()
        if 'visibility' in cleaned_data and \
            cleaned_data['visibility'] != "restricted" and \
            "assignees_groups" in cleaned_data and \
            hasattr(cleaned_data["assignees_groups"], "none") and \
            callable(getattr(cleaned_data["assignees_groups"], "none")):
            cleaned_data["assignees_groups"] = cleaned_data["assignees_groups"].none()
        return cleaned_data
