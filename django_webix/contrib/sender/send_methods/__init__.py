def get_default_user_cost(self, send_method: [str], request=None, *args, **kwargs):
    """
    Get default user cost

    :param self: a user instance
    :param send_method: str of send method
    :param args: Optional arguments
    :param kwargs: optional keyword arguments
    :param request:
    :return: value of cost
    """

    from django_webix.contrib.sender.utils import get_config_from_settings

    method, _ = send_method.split(".", 1)
    method_config = get_config_from_settings(method, request)

    return method_config.get("cost", 0.0)
