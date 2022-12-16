from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django_webix.contrib.commands_manager.forms import CommandExecutionFormCreate, CommandExecutionFormUpdate
from django_webix.contrib.commands_manager.models import CommandExecution
from django_webix.views import (WebixUpdateView, WebixListView, WebixCreateView, WebixDeleteView)

from django.utils.html import escapejs
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

class CommandExecutionMixin:
    def get_model_name(self):
        return 'dwcommands_manager.commandexecution'

@method_decorator(login_required, name='dispatch')
class CommandExecutionListView(CommandExecutionMixin, WebixListView):
    model = CommandExecution
    enable_json_loading = True
    template_name = 'django_webix/commands_manager/list.js'
    actions = []

    def get_fields(self):
        _fields = [
            {
                'field_name': 'command_name',
                'datalist_column': format_lazy(
                    '''{{
                    id: "command_name",
                    serverFilterType: "icontains",
                    header: ["{}", {{content: "serverFilter"}}],
                    sort:"server",
                    adjust: "all",
                    fillspace: true
                    }}''',
                    escapejs(_("Command name")))
            },
            {
                'field_name': 'description',
                'datalist_column': format_lazy(
                    '''{{
                    id: "description",
                    serverFilterType: "icontains",
                    header: ["{}", {{content: "serverFilter"}}],
                    adjust: "all",
                    fillspace: true,
                    sort: "server"
                    }}''',
                    escapejs(_("Description")))
            },
            {
                'field_name': 'last_execution_date',
                'datalist_column': format_lazy(
                    '''{{
                    id: "last_execution_date",
                    serverFilterType: "icontains",
                    header: ["{}", {{content: "serverFilter"}}],
                    adjust: "all",
                    fillspace: true,
                    sort: "server",
                    format:function(value){{if(value != ''){{valuearr = value.split("T")[0].split('-'); valuearr2 = value.split("T")[1].split(':');value = valuearr[2] + '/' + valuearr[1] + '/' + valuearr[0] + ' ' + valuearr2[0] + ':' + valuearr2[1];return value;}} return value;}}
                    }}''',
                    escapejs(_("Last ex. date")))
            },
            {
                'field_name': 'last_execution_state',
                'datalist_column': format_lazy(
                    '''{{
                    id: "last_execution_state",
                    serverFilterType: "icontains",
                    header: ["{}", {{content: "serverFilter"}}],
                    adjust: "all",
                    fillspace: true,
                    sort: "server"
                    }}''',
                    escapejs(_("Last ex. state")))
            },
            {
                'field_name': 'id',
                'click_action': '''command_execute(el['id'])''',
                'datalist_column': format_lazy(
                    '''{{
                    id: "id",
                    header: [{{text: "{}", css: {{'text-align': 'center'}} }}],
                    width: 70,
                    template: '<i style="cursor:pointer" class="webix_icon far fa-play"></i>', css: {{'text-align': 'center'}}
                    }}''',
                    escapejs(_("Execute")))
            },
        ]
        return super().get_fields(fields = _fields)


@method_decorator(login_required, name='dispatch')
class CommandExecutionUpdateView(CommandExecutionMixin, WebixUpdateView):
    model = CommandExecution
    form_class = CommandExecutionFormUpdate
    template_name = 'django_webix/commands_manager/update.js'


@method_decorator(login_required, name='dispatch')
class CommandExecutionCreateView(CommandExecutionMixin, WebixCreateView):
    model = CommandExecution
    form_class = CommandExecutionFormCreate
    template_name = 'django_webix/commands_manager/create.js'


@method_decorator(login_required, name='dispatch')
class CommandExecutionDeleteView(CommandExecutionMixin, WebixDeleteView):
    model = CommandExecution
