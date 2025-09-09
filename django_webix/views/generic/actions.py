import io
import json
import os
import zipfile
from wsgiref.util import FileWrapper

from django.db import models
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django_webix.views import WebixTemplateView
from django_webix.views.generic.decorators import action_config
from django_webix.views.generic.utils import NestedObjectsWithLimit, tree_formatter


class DeleteRelatedObjectsView(WebixTemplateView):
    """
    A custom view for displaying related objects that will be deleted and any potential errors.

    This view extends `WebixTemplateView` and is used to render a JavaScript template
    (`action_deleterelatedobjects.js`). It prepares the context data required to show the user
    the related objects that will be deleted and any errors that might occur during deletion.

    Attributes:
        template_name (str): The path to the JavaScript template used for rendering.
    """

    template_name = "django_webix/include/action_deleterelatedobjects.js"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = kwargs.get("queryset")

        # Check failure delete related objects
        failure_delete_related_objects = []
        model_related_objects = getattr(queryset.model, "get_failure_delete_related_objects", None)
        if model_related_objects is not None:
            for item in queryset:
                failure_delete_related_objects += model_related_objects(request=self.request, obj=item)
        context["failure_delete_related_objects"] = failure_delete_related_objects

        # Collect related objects
        collector = NestedObjectsWithLimit(using="default")
        collector.collect(queryset)
        context["related_objects"] = json.dumps(tree_formatter(collector.nested()))
        context["related_summary"] = [
            {"model_name": str(k._meta.verbose_name_plural), "count": len(collector.data[k])}
            for k in collector.data.keys()
        ]
        return context


@action_config(
    action_key="delete",
    response_type="json",
    short_description=_("Delete"),
    allowed_permissions=["delete"],
    reload_list=True,
    template_view=DeleteRelatedObjectsView,
)
def multiple_delete_action(self, request, qs):
    """
    Deletes multiple objects and returns a JSON response with the result.

    This action is configured to delete selected objects and requires the `delete` permission.
    It returns a JSON response indicating the success of the operation and the number of deleted objects.

    Args:
        self: Reference to the instance of the class containing this action.
        request: The HTTP request object.
        qs: The queryset of objects to be deleted.

    Returns:
        JsonResponse: A JSON response containing:
            - `status`: Boolean indicating whether the operation was successful.
            - `message`: A confirmation message with the number of deleted objects.
            - `redirect_url`: The URL to redirect to after deletion.
    """
    _count_delete_instances = int(qs.only(qs.model._meta.pk.name).count())
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


@action_config(
    action_key="download_attachments",
    response_type="blank",
    short_description=_("Download all attachments"),
    allowed_permissions=["view"],
    reload_list=False,
)
def multiple_download_attachments(self, request, qs):
    """
    Downloads all file and image attachments associated with the selected objects.

    This action creates a ZIP file containing all attachments (files or images) from the selected objects.
    It requires the `view` permission and opens the ZIP file in a new browser tab for download.

    Args:
        self: Reference to the instance of the class containing this action.
        request: The HTTP request object.
        qs: The queryset of objects whose attachments will be downloaded.

    Returns:
        HttpResponse: An HTTP response with the ZIP file attached, forcing the browser to download it.
    """
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
                    if obj.name != "" and obj.storage.exists(obj.name):
                        data = obj.read()
                        zip_file.writestr(f"{name_element}/{os.path.basename(obj.name)}", data)
        zip_file.close()

    filepath = "all_attachments.zip"
    zip_buffer.seek(0)
    wrapper = FileWrapper(zip_buffer)
    response = HttpResponse(wrapper, content_type="application/force-download")
    response["Content-Disposition"] = "inline; filename=" + filepath
    zip_buffer.close()
    return response
