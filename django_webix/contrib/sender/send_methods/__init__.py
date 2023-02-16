from django.conf import settings


def get_default_user_cost(self, send_method:[str], *args, **kwargs):
    """
    Get default user cost

    :param self: a user instance
    :param send_method: str of send method
    :param args: Optional arguments
    :param kwargs: optional keyword arguments
    :return: value of cost
    """
    method_config = next((i for i in settings.WEBIX_SENDER['send_methods'] if f"{i['method']}.{i['function']}" == send_method))['config']
    return method_config.get('cost', 0.0)
