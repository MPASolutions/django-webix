from django.urls import path

from django_webix.contrib.commands_manager.views import (CommandExecutionListView,
                                                         CommandExecutionUpdateView,
                                                         CommandExecutionCreateView,
                                                         CommandExecutionDeleteView)
from django_webix.contrib.commands_manager.views_js import CommandExecute, CommandParameters

urlpatterns = [
    path('commands_manager/command_execution/list',
         CommandExecutionListView.as_view(),
         name='dwcommands_manager.commandexecution.list'),
    path('commands_manager/command_execution/<int:pk>/update',
         CommandExecutionUpdateView.as_view(),
         name='dwcommands_manager.commandexecution.update'),
    path('commands_manager/command_execution/create',
         CommandExecutionCreateView.as_view(),
         name='dwcommands_manager.commandexecution.create'),
    path('commands_manager/command_execution/<int:pk>/delete',
         CommandExecutionDeleteView.as_view(),
         name='dwcommands_manager.commandexecution.delete'),
    path('commands_manager/parameters/<str:command_name>',
         CommandParameters.as_view(),
         name='dwcommands_manager.commandexecution.parameters'),
    path('commands_manager/command_execution/<int:pk>/execute',
         CommandExecute.as_view(),
         name='dwcommands_manager.commandexecution.execute'),
]
