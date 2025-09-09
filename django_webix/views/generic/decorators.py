import json

from django.apps import apps
from django.http import JsonResponse, QueryDict
from django.utils.translation import gettext_lazy as _
from django_webix.views import WebixFormView, WebixTemplateView


class DynamicTemplateFormView(WebixFormView):
    """
    A dynamic form view for rendering Webix templates with additional context data for actions

    This class extends `WebixFormView` to provide dynamic template rendering capabilities.
    It includes the `queryset` and `parent_view` in the context data for further processing.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queryset"] = kwargs.get("queryset")
        context["parent_view"] = kwargs.get("parent_view")
        return context


def action_config(
    action_key,
    response_type,
    allowed_permissions=None,
    short_description=None,
    modal_header=_("Fill in the form"),
    modal_title=_("Are you sure you want to proceed with this action?"),
    modal_click=_("Go"),
    modal_ok=_("Proceed"),
    modal_cancel=_("Undo"),
    form=None,
    reload_list=True,
    maximum_count=None,
    template_view=None,
    dynamic=False,
    form_view=DynamicTemplateFormView,
    form_view_template=None,
    group=None,
    icon=None,
):  # TODO: permission check before execution
    """
    A decorator to configure actions on a list view.

    This decorator configures actions such as CRUD operations, form submissions, or custom actions
    on a list of objects. It supports dynamic rendering, permission checks, and various response types.

    Args:
        action_key (str): A unique identifier for the action.
        response_type (str): The type of HTTP response. Options: 'json', 'script', or 'blank'.
        allowed_permissions (list, optional): A list of permissions required to execute the action.
        short_description (str, optional): A short description of the action for display purposes.
        modal_header (str, optional): The title of the modal header. Defaults to "Fill in the form".
        modal_title (str, optional): The description displayed in the modal. Defaults to a confirmation message.
        modal_click (str, optional): The text for the form confirmation button. Defaults to "Go".
        modal_ok (str, optional): The text for the confirmation button. Defaults to "Proceed".
        modal_cancel (str, optional): The text for the cancel button. Defaults to "Undo".
        form (Form, optional): The form to display before executing the action.
        reload_list (bool, optional): Whether to reload the list after executing the action. Defaults to `True`.
        maximum_count (int, optional): The maximum number of selected elements allowed for the action.
        template_view (TemplateView, optional): A `TemplateView` to render before executing the action.
        dynamic (bool, optional): Whether the action should be dynamically loaded. Defaults to `False`.
        form_view (FormView, optional): A `FormView` for dynamically rendering the action window.
            Defaults to `DynamicTemplateFormView`.
        form_view_template (str, optional): The template for dynamically rendering the action window.
        group (str, optional): A text label for grouping actions.
        icon (str, optional): The Font Awesome icon class for the action.

    Returns:
        function: A decorator function that wraps the action function and configures its behavior.

    Raises:
        Exception: If `response_type` is not one of 'json', 'script', or 'blank'.
        Exception: If `template_view` is not a subclass of `WebixTemplateView`.
        Exception: If `form_view` is not a subclass of `WebixFormView`.

    Notes:
        - For `response_type="json"`, the response should be a `JsonResponse` with keys:
            - `status`: A boolean indicating success.
            - `message`: A message to display.
            - `message_on_popup`: A boolean indicating whether to show the message as a popup.
            - `message_type`: The type of message (e.g., 'info', 'error').
        - For `response_type="script"`, the response should be an `HttpResponse` with JavaScript content.
        - For `response_type="blank"`, the response can be any type of `HttpResponse`.
    """

    if allowed_permissions is None:
        allowed_permissions = []

    if response_type not in ["json", "script", "blank"]:
        raise Exception("No valid response_type [json,script,blank]")

    if template_view is not None and not issubclass(template_view, WebixTemplateView):
        raise Exception("No valid template_view class, it must be subclass of WebixTemplateView")

    if form_view is not None and not issubclass(form_view, WebixFormView):
        raise Exception("No valid form_view class, it must be subclass of WebixFormView")

    def decorator(func):
        def wrapper(self, request, qs):

            if maximum_count is not None and qs.only(qs.model._meta.pk.name).count() > maximum_count:
                return JsonResponse(
                    {
                        "status": False,
                        "errors": [_("You can perform this action on a maximum of {} raws").format(maximum_count)],
                    },
                    status=400,
                )

            if template_view is not None and request.method == "POST" and request.POST.get("template_view"):
                request.method = "GET"  # convert request from POST to GET

                def get_context_data_webix_base(self, request, **kwargs):
                    context = super(template_view, self).get_context_data_webix_base(request, **kwargs)
                    context["action_key"] = action_key
                    context["webix_container_id"] = f"{action_key}_win_body"
                    return context

                template_view.get_context_data_webix_base = get_context_data_webix_base

                return template_view.as_view()(request, queryset=qs, action_key=action_key)

            elif dynamic is not None and request.method == "POST" and request.POST.get("dynamic"):
                request.method = "GET"  # convert request from POST to GET

                def get_context_data_webix_base(self, request, **kwargs):
                    context = super(form_view, self).get_context_data_webix_base(request, **kwargs)
                    context.update(
                        {
                            "ids": request.POST.get("ids"),
                            "all": request.POST.get("all"),
                            "action_key": action_key,
                            "response_type": response_type,
                            "short_description": short_description,
                            "modal_header": modal_header,
                            "modal_title": modal_title,
                            "modal_click": modal_click,
                            "modal_ok": modal_ok,
                            "modal_cancel": modal_cancel,
                            "reload_list": reload_list,
                            # 'form': form # form is passed by view by default with all data filled-in
                        }
                    )
                    context["webix_container_id"] = f"{action_key}_win"

                    return context

                form_view.get_context_data_webix_base = get_context_data_webix_base

                form_view.template_name = (
                    "django_webix/include/action_dynamic.js" if form_view_template is None else form_view_template
                )

                form_view.form_class = form

                return form_view.as_view()(request, queryset=qs, parent_view=self, action_key=action_key)

            elif form is not None and request.method == "POST":
                try:
                    params = QueryDict(mutable=True)
                    params.update(json.loads(request.POST.get("params", "{}")))
                except json.JSONDecodeError:
                    params = QueryDict()

                _form = form(params, request.FILES, request=request, **{"queryset": qs})
                if _form.is_valid():
                    anonymous = (
                        request.user.is_anonymous()
                        if callable(request.user.is_anonymous)
                        else request.user.is_anonymous
                    )
                    if not anonymous and apps.is_installed("django.contrib.admin"):
                        from django.contrib.admin.models import CHANGE, LogEntry
                        from django.contrib.contenttypes.models import ContentType

                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                            object_id=None,  # on a QS
                            object_repr=",".join([str(i) for i in qs.values_list("pk", flat=True)]),
                            action_flag=CHANGE,
                            change_message=_("Action success: {} data:{}").format(
                                wrapper.short_description, _form.cleaned_data
                            ),
                        )

                    return func(self, request, qs, _form)
                else:
                    return JsonResponse(
                        {
                            "status": False,
                            "errors": [{"label": None, "error": error} for error in _form.non_field_errors()]
                            + [{"label": field.label, "error": error} for field in _form for error in field.errors],
                        },
                        status=400,
                    )
            else:
                anonymous = (
                    request.user.is_anonymous() if callable(request.user.is_anonymous) else request.user.is_anonymous
                )
                if not anonymous and apps.is_installed("django.contrib.admin"):
                    from django.contrib.admin.models import CHANGE, LogEntry
                    from django.contrib.contenttypes.models import ContentType

                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(qs.model).pk,
                        object_id=None,  # on a QS
                        object_repr=",".join([str(i) for i in qs.values_list("pk", flat=True)]),
                        action_flag=CHANGE,
                        change_message=_("Action success: {}").format(wrapper.short_description),
                    )

            return func(self, request, qs)

        # Attach metadata to the wrapper function
        setattr(wrapper, "action_key", action_key)
        setattr(wrapper, "response_type", response_type)
        setattr(wrapper, "allowed_permissions", allowed_permissions)
        setattr(wrapper, "short_description", short_description)
        setattr(wrapper, "modal_header", modal_header)
        setattr(wrapper, "modal_title", modal_title)
        setattr(wrapper, "modal_click", modal_click)
        setattr(wrapper, "modal_ok", modal_ok)
        setattr(wrapper, "modal_cancel", modal_cancel)
        setattr(wrapper, "form", form)
        setattr(wrapper, "reload_list", reload_list)
        setattr(wrapper, "maximum_count", maximum_count)
        setattr(wrapper, "template_view", template_view)
        setattr(wrapper, "dynamic", dynamic)
        setattr(wrapper, "form_view", form_view)
        setattr(wrapper, "form_view_template", form_view_template)
        setattr(wrapper, "group", group)
        setattr(wrapper, "icon", icon)
        return wrapper

    return decorator
