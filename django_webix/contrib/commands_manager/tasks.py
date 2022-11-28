import datetime
import importlib
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.utils.translation import gettext_lazy as _

from django_webix.contrib.commands_manager.models import CommandExecution

app = importlib.import_module(getattr(settings, 'CELERY_APP', getattr(settings, 'DJANGO_WEBIX_COMMANDS_MANAGER_APP_CELERY'))).app


def _ord(e):
    if 'pos_id' in e:
        return e['pos_id']
    return 100


@app.task(name='Execute command')
def execute_command_task(ce_id):
    ce = CommandExecution.objects.filter(id=ce_id).first()
    if ce is None:
        raise Exception(_('Command execution id is not valid'))
    else:
        parameters_pos = []
        parameters = []

        par = ce.parameters
        par.sort(key=_ord)

        for el in par:
            if el['field_name'] != 'help':
                if 'pos_id' in el:
                    if 'value' in el:
                        parameters_pos.append(str(el['value']))
                else:
                    if el['data_type'] == 'bool':
                        if 'value' in el and el['value'] == 1:
                            parameters.append(el['field_name'])
                    elif el['data_type'] == 'date':
                        if 'value' in el and str(el['value']).strip() != '':
                            parameters.append(el['field_name'] + '=' + datetime.date.fromisoformat(
                                el['value'].split('Z')[0]).strftime("%m/%d/%Y"))
                    else:
                        if 'value' in el and str(el['value']).strip() != '':
                            parameters.append(el['field_name'] + '=' + str(el['value']))

        out = StringIO()

        try:
            call_command(ce.command_name, parameters_pos, parameters, stdout=out, stderr = out)
            ce.last_execution_state = 'finished'
            ce.output = out.getvalue()
            ce.save()
        except Exception as e:
            ce.last_execution_state = 'error'
            ce.output = out.getvalue() + '\n' + str(e)
            ce.save()
            raise Exception(e)
