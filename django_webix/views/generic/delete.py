import copy
import json

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import DeleteView
from django_webix.views.generic.base import WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin
from django_webix.views.generic.signals import django_webix_view_post_delete, django_webix_view_pre_delete
from django_webix.views.generic.utils import NestedObjectsWithLimit, tree_formatter

try:
    from django.utils.encoding import force_text as force_str
except ImportError:
    from django.utils.encoding import force_str


class WebixDeleteView(WebixBaseMixin, WebixPermissionsMixin, WebixUrlMixin, DeleteView):
    logs_enable = True
    exclude_models = None
    only_models = None

    template_name = "django_webix/generic/delete.js"

    def get_exclude_models(self):
        return self.exclude_models

    def get_only_models(self):
        return self.only_models

    def get_object(self, queryset=None):
        if getattr(self, "object", None) is not None:
            return self.object
        return super(WebixDeleteView, self).get_object(queryset=queryset)

    def get_json(self):
        context = self.get_context_data(object=self.object)
        return JsonResponse(
            {
                "has_delete_permission": context["has_delete_permission"],
                "info_no_delete_permission": context["info_no_delete_permission"],
            }
        )

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.request.method == "GET":
            if self.request.GET.get("json", None) is not None:
                return self.get_json()
            if not self.has_view_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_("View permission is not allowed"))
        else:
            if not self.has_delete_permission(request=self.request, obj=self.object):
                raise PermissionDenied(_("Delete permission is not allowed"))
        return super(WebixDeleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WebixDeleteView, self).get_context_data(**kwargs)
        context.update(self.get_context_data_webix_permissions(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_url(request=self.request, obj=self.object))
        context.update(self.get_context_data_webix_base(request=self.request))
        context.update({"multiple_delete_confirmation": getattr(settings, "WEBIX_MULTIPLE_DELETE_CONFIRMATION", True)})
        # Nested objects
        collector = NestedObjectsWithLimit(
            using="default", exclude_models=self.get_exclude_models(), only_models=self.get_only_models()
        )
        collector.collect([self.object])
        context.update(
            {
                "related_objects": json.dumps(tree_formatter(collector.nested())),
            }
        )
        context["related_summary"] = [
            {"model_name": str(k._meta.verbose_name_plural), "count": len(collector.data[k])}
            for k in collector.data.keys()
        ]

        return context

    def get_success_url(self, next_step=None):
        if self.success_url is not None:
            url = self.success_url
        elif self.get_url_list() is not None:
            url = self.get_url_list()
            if "?" in url:
                url += "&full_state"
            else:
                url += "?full_state"
        else:
            raise ImproperlyConfigured(
                _("No URL to redirect to.  Either provide a url or define" " a get_absolute_url method on the Model.")
            )
        return url

    def get_failure_url(self):
        if self.failure_url:
            url = self.failure_url
        elif self.get_delete(obj=self.object) is not None:
            url = self.get_delete(obj=self.object)
        else:
            raise ImproperlyConfigured(
                _(
                    "No URL to failure redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model."
                )
            )
        return url

    def pre_delete_valid(self, **kwargs):
        django_webix_view_pre_delete.send(sender=self, instance=self.object)

    def post_delete_valid(self, **kwargs):
        django_webix_view_post_delete.send(sender=self, instance=self.copied_object)

    def response_valid(self, success_url=None, **kwargs):
        if success_url is not None:
            if "?" in success_url:
                success_url += f"?state={success_url}"
            else:
                success_url += ""
        return HttpResponseRedirect(success_url)

    def response_invalid(self, failure_url=None, **kwargs):
        return HttpResponseRedirect(failure_url)

    def form_valid(self, form):
        return self.delete(request=self.request)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.copied_object = copy.deepcopy(self.object)

        # noinspection PyCallingNonCallable
        anonymous = request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
        if len(self.get_failure_delete_related_objects(request=request, obj=self.object)) > 0:
            return self.response_invalid(failure_url=self.get_failure_url())

        if self.logs_enable is True and not anonymous and apps.is_installed("django.contrib.admin"):
            from django.contrib.admin.models import DELETION, LogEntry
            from django.contrib.contenttypes.models import ContentType

            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(self.object).pk,
                object_id=self.object.pk,
                object_repr=force_str(self.object),
                action_flag=DELETION,
            )

        self.pre_delete_valid()

        success_url = self.get_success_url()
        self.object.delete()
        self.post_delete_valid()

        return self.response_valid(success_url=success_url)
