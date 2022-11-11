from django.apps import AppConfig
from django.conf import settings

def check_settings():
    # check webix version
    if not hasattr(settings, 'WEBIX_VERSION'):
        raise Exception('WEBIX_VERSION is not found in your settings (eg.9.4.0)')

    # check webix license (we have to disable some form controls)
    # in accord to https://docs.webix.com/desktop__controls.html
    if not hasattr(settings, 'WEBIX_LICENSE'):
        raise Exception('WEBIX_LICENSE is not found in your settings ("FREE" or "PRO")')

    # check webix container id
    if not hasattr(settings, 'WEBIX_CONTAINER_ID'):
        raise Exception('WEBIX_CONTAINER_ID is webix_id where js interfaces are loaded and '
                        'is not found in your settings (usually "content_right")')


class DjangoWebixConfig(AppConfig):
    name = 'django_webix'

    def ready(self):
        check_settings()
