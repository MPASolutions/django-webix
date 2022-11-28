from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _



class CommandExecution(models.Model):
    description = models.CharField(_('Description'), max_length=64)
    command_name = models.CharField(_('Command name'), max_length=64,
                                    choices=[(i, i) for i in settings.COMMANDS_MANAGER_ENABLED])
    parameters = models.JSONField(_('Parameters'), blank=True, null=True)
    insert_date = models.DateTimeField(_('Insert date'), auto_now_add=True)
    last_execution_date = models.DateTimeField(_('Last Execution'), blank=True, null=True)
    last_execution_state = models.CharField(max_length=32, choices=(
        ('started', _('Started')),
        ('error', _('Error')),
        ('finished', _('Finished')),
        ('unknown', _('Unknown'))
    ), default='unknown')
    output = models.TextField(_('Output'), blank=True, null=True)

    class Meta:
        verbose_name = _('Command execution')
        verbose_name_plural = _('Commands executions')

    def __str__(self):
        return self.command_name + ': ' + self.description
