import datetime
# noinspection PyUnresolvedReferences
from argparse import _StoreTrueAction, _StoreFalseAction

from django.contrib.auth.decorators import login_required
from django.core.management import get_commands, load_command_class
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from django_webix.contrib.commands_manager.models import CommandExecution
from django_webix.contrib.commands_manager.tasks import execute_command_task


# example fields command parameters
# arguments = [
#     {
#         'field_name' : '', # must match the parameter definition
#         'data_type': 'int', # type of field displayed: int (does not expect null, use string), string, bool, combo, date
#         'value': '' # optional, default value, on bool put 0/1
#         'options' : [' ', 'ATTUALE', 'PUBBLICATO'], # on combo only, leave option with space to allow null
#         'pos_id' : id # only for position them with position number, for these field_name it is only visual
#     },
# ]

def arg_elaborate(arg, par):
    if arg.help:
        par['help'] = arg.help
    if arg.choices is not None:
        par['data_type'] = 'choice'
        if arg.required:
            par['options'] = arg.choices
            par['value'] = arg.choices[0]
        else:
            op = arg.choices
            op.append(' ')
            par['options'] = op
            par['value'] = ' '
    elif arg.type is int:
        if arg.required:
            par['data_type'] = 'int'
        else:
            par['data_type'] = 'string'
        if arg.default:
            par['value'] = arg.default
    elif type(arg) is _StoreTrueAction or type(arg) is _StoreFalseAction:
        par['data_type'] = 'bool'
        par['value'] = 0
    else:
        par['data_type'] = 'string'
        if arg.default:
            par['value'] = arg.default
    return par


# for use direct parameters
# if hasattr(command, 'arguments'):
#     return JsonResponse({'parameters': command.arguments}, safe=False)

@method_decorator(login_required, name='dispatch')
class CommandParameters(DetailView):
    def get_object(self, queryset=None):
        command_name = self.kwargs.get('command_name')
        if command_name not in get_commands():
            raise Http404(_("Invalid command name"))
        else:
            return command_name

    def get(self, request, *args, **kwargs):
        command_name = self.get_object()
        app_name = get_commands()[command_name]
        command = load_command_class(app_name, command_name)
        pars = command.create_parser(app_name, command_name)
        args_p = pars._action_groups[0]._group_actions
        args = pars._action_groups[1]._group_actions[9:]
        params = []
        for _id, arg_p in zip(range(len(args_p)), args_p):
            par = {
                'field_name': arg_p.dest,
                'pos_id': _id
            }
            arg_elaborate(arg_p, par)
            params.append(par)
        for arg in args:
            par = {
                'field_name': arg.option_strings[-1],
            }
            arg_elaborate(arg, par)
            params.append(par)
        if hasattr(command, 'help'):
            params.append({
                'field_name': 'help',
                'value': command.help
            })
        return JsonResponse({'parameters': params}, safe=False)


@method_decorator(login_required, name='dispatch')
class CommandExecute(DetailView):
    model = CommandExecution
    def get(self, request, *args, **kwargs):
        ce = self.get_object()
        ce.last_execution_state = 'started'
        ce.last_execution_date = datetime.datetime.now()
        ce.save()
        execute_command_task.delay(ce.id)
        return JsonResponse({'status': True}, safe=False)
