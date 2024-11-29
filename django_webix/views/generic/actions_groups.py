from django.utils.translation import gettext_lazy as _


class ActionsGroup:
    order = 0
    name = None
    icon = ""

    def __init__(self, order=0, name=None, icon="", **kwargs):
        self.order = order
        self.name = name
        self.icon = icon


actions_group_export = ActionsGroup(order=999, name=_("Exports"), icon="far fa-file-export")

actions_group_webgis = ActionsGroup(order=999, name=_("Webgis"), icon="far fa-globe-pointer")
