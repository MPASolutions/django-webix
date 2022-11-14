from django_webix.forms import WebixModelForm
from django_webix.contrib.commands_manager.models import CommandExecution
from django.utils.translation import gettext_lazy as _

class CommandExecutionFormCreate(WebixModelForm):
    label_width = 150

    class Meta:
        model = CommandExecution
        localized_fields = '__all__'
        fields = ['description', 'command_name', 'parameters']

    def get_fieldsets(self, fs=None):
        if fs is None: fs = self.get_elements

        return [

            {'cols': [fs['description']]},
            {'cols': [fs['command_name']]},

            {'cols': [{'id': 'command_help', 'height':20, 'rows':[]}]},
            {'cols': [
                {'id': 'form_parameters', 'rows':[{}]},
                {'width':100},
                fs['parameters']]},
        ]

class CommandExecutionFormUpdate(WebixModelForm):
    label_width = 150

    class Meta:
        model = CommandExecution
        localized_fields = '__all__'
        fields = ['description', 'command_name', 'parameters',
                  'last_execution_date','last_execution_state', 'output']

    def get_fieldsets(self, fs=None):
        if fs is None: fs = self.get_elements

        for field_name in ['last_execution_date','last_execution_state']:
            fs[field_name].update({'readonly': 'readonly', 'disabled': True})

        fs['output'].update({'readonly': 'readonly', 'labelWidth': 0})

        return [
            {
                'view': 'tabview',
                'cells': [
                    {
                        'header': _('Parameters'),
                        'rows':[
                            {'cols': [fs['description']]},
                            {'cols': [fs['command_name']]},

                            {'cols': [{'id': 'command_help', 'height':20, 'rows':[]}]},
                            {'cols': [
                                {'id': 'form_parameters', 'rows':[{}]},
                                {'width':100},
                                fs['parameters']]},

                            {'cols': [fs['last_execution_date'], fs['last_execution_state']]},
                        ]
                    },
                    {
                        'header': _('Output'),
                        'rows': [
                            {'cols': [fs['output']]},
                        ]
                    }
                ]
            }
        ]

