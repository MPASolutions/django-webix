# -*- coding: utf-8 -*-

import os
import io
import sys
import zipfile
import mimetypes
from wsgiref.util import FileWrapper
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _

from django_webix.views.generic.decorators import action_config


@action_config(action_key='delete',
               response_type='json',
               short_description=_('Delete'),
               allowed_permissions=['delete'],
               reload_list=True)
def multiple_delete_action(self, request, qs):
    _count_delete_instances = int(qs.count())
    qs.delete()
    return JsonResponse({
        "status": True,
        "message": _('{count_delete_instances} elements have been deleted').format(
            count_delete_instances=_count_delete_instances),
        "redirect_url": self.get_url_list(),
    }, safe=False)


@action_config(action_key='download_attachments',
               response_type='blank',
               short_description=_('Download all attachments'),
               allowed_permissions=['view'],
               reload_list=False)
def multiple_download_attachments(self, request, qs):
    fields = []
    for fi in qs.model._meta.fields:
        if isinstance(fi, models.FileField) or isinstance(fi, models.ImageField):
            fields.append(fi.name)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for element in qs:
            name_element = str(element)
            for field in fields:
                if hasattr(element, field):
                    obj = getattr(element, field)
                    if obj.name != '' and obj.storage.exists(obj.name):
                        data = obj.read()
                        zip_file.writestr(f"{name_element}/{os.path.basename(obj.name)}", data)
        zip_file.close()

    filepath = 'all_attachments.zip'
    zip_buffer.seek(0)
    wrapper = FileWrapper(zip_buffer)
    response = HttpResponse(wrapper, content_type='application/force-download')
    response['Content-Disposition'] = 'inline; filename=' +filepath
    zip_buffer.close()
    return response
