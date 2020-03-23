from django.http import JsonResponse
from django.utils.translation import ugettext as _


def multiple_delete_action(self, request, qs):
    _count_delete_instances = int(qs.count())
    qs.delete()
    return JsonResponse({
        "message": _('{count_delete_instances} elements have been deleted').format(count_delete_instances = _count_delete_instances)
    }, safe=False)


multiple_delete_action.verbose_name = _('Delete')
multiple_delete_action.short_description = _('Delete')
multiple_delete_action.allowed_permissions = ('delete',)
