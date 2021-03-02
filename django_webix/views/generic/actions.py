# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django_webix.views.generic.decorators import action_config


@action_config(action_key='delete',
               response_type='json',
               short_description=_('Delete'),
               allowed_permissions=['delete'])
def multiple_delete_action(self, request, qs):
    _count_delete_instances = int(qs.count())
    qs.delete()
    return JsonResponse({
        "status": True,
        "message": _('{count_delete_instances} elements have been deleted').format(
            count_delete_instances=_count_delete_instances),
        "redirect_url": self.get_url_list(),
    }, safe=False)
