import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from mpadjango.db.models import MpaModel as Model
except ImportError:
    from django.db.models import Model

class ImportFile(Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allegato = models.FileField(verbose_name=_('Attachment'), upload_to='import_file', blank=True, null=True)
