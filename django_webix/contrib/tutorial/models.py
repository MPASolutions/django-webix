
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

try:
    from mpadjango.db.models import MpaModel as Model
except ImportError:
    from django.db.models import Model


class TutorialArea(Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Tutorial area')
        verbose_name_plural = _('Tutorial areas')
        ordering = ['name']

    def __str__(self):
        return "{}".format(self.name)


class TutorialItem(Model):
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    url = models.URLField('URL', max_length=255)
    tutorial_type = models.CharField(_('Tutorial type'), max_length=32, choices=[
        ('pdf', _('PDF')),
        ('video', _('Video'))
    ])
    target = models.CharField(_('Type of opening file'), max_length=32, choices=(
        ('iframe', _('Modal with iframe')),
        ('_self', _('Same window')),
        ('_blank', _('New tab'))
    ), default='_self')
    area = models.ForeignKey(TutorialArea, verbose_name=_('Area'),
                             blank=True, null=True, on_delete=models.CASCADE)

    visible_from = models.DateField(_('Visible from'), blank=True, null=True)
    visible_to = models.DateField(_('Visible to'), blank=True, null=True)

    class Meta:
        verbose_name = _("Tutorial item")
        verbose_name_plural = _("Tutorial items")
        ordering = ['name']

    def __str__(self):
        return "{}: {}".format(self.get_tutorial_type_display(), self.name)
