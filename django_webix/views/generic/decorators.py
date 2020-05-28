from django.utils.translation import ugettext as _


def action_config(
    action_key,
    response_type,
    allowed_permissions=[],
    short_description=None,
    modal_title=_("Are you sure you want to proceed with this action?"),
    modal_ok=_("Proceed"),
    modal_cancel=_("Undo"),
):  # TODO: permission check bebore execution

    if response_type not in ['json', 'script', 'blank']:
        raise Exception('No valid response_type [json,script,blank]')

    def decorator(func):
        def wrapper(self, request, qs):
            return func(self, request, qs)

        setattr(wrapper, 'action_key', action_key)
        setattr(wrapper, 'response_type', response_type)
        setattr(wrapper, 'allowed_permissions', allowed_permissions)
        setattr(wrapper, 'short_description', short_description)
        setattr(wrapper, 'modal_title', modal_title)
        setattr(wrapper, 'modal_ok', modal_ok)
        setattr(wrapper, 'modal_cancel', modal_cancel)

        return wrapper

    return decorator
