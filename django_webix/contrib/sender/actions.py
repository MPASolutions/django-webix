from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django_webix.views.generic.actions import DeleteRelatedObjectsView
from django_webix.views.generic.decorators import action_config


@action_config(
    action_key="delete",
    response_type="json",
    short_description=_("Delete"),
    allowed_permissions=["delete"],
    reload_list=True,
    template_view=DeleteRelatedObjectsView,
)
def multiple_delete_messagesent_action(self, request, qs):
    _count_delete_instances = int(qs.only(qs.model._meta.pk.name).count())
    for method in ["telegram", "email", "skebby"]:
        if qs.filter(send_method__icontains=method).exists():
            return JsonResponse(
                {
                    "status": False,
                    "message": _("Data was not deleted because some was sent with the {method} method").format(
                        method=method
                    ),
                },
                safe=False,
            )

    qs.delete()
    return JsonResponse(
        {
            "status": True,
            "message": _("{count_delete_instances} elements have been deleted").format(
                count_delete_instances=_count_delete_instances
            ),
            "redirect_url": self.get_url_list(),
        },
        safe=False,
    )
