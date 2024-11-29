from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import translation
from django_webix.contrib.admin.models import WebixAdminMenu, WebixAdminMenuLanguage


def create_menu(parent, nodes, debug):
    for node in nodes:
        model = None
        if node[0] is not None:
            mod = node[0].split(".")
            extra = {}
            if len(mod) > 1:
                extra = {"app_label": mod[-2]}

            model = ContentType.objects.filter(model=mod[-1], **extra).first()

        m = None

        if debug:
            print(model if model is not None else node[1])
        else:
            m = WebixAdminMenu(
                model=model,
                label=node[1],
                icon=node[2],
                url=node[3],
                prefix=node[4],
                active_all=node[5],
                parent=parent,
            )
            m.save()
            m.groups.add(*Group.objects.filter(name__in=node[6]))

            if len(settings.LANGUAGES) > 1 and node[1] is not None:
                for abbreviation, language in settings.LANGUAGES:
                    with translation.override(abbreviation):
                        WebixAdminMenuLanguage.objects.create(menu=m, language=abbreviation, label=node[1])

        create_menu(m, node[7], debug)


class Command(BaseCommand):
    """
    python manage.py set_admin_menu
    """

    help = "command to set the django-webix admin menus"

    def add_arguments(self, parser):
        parser.add_argument(
            "--debug", action="store_true", help="prints the menus that would be created without making the change"
        )
        parser.add_argument("--no_clean", action="store_true", help="do not delete existing menus")

    def handle(self, *args, **options):
        debug = False
        if options["debug"]:
            debug = True

        if not debug and not options["no_clean"]:
            self.stdout.write("deleting menu")
            WebixAdminMenu.objects.all().delete()
            WebixAdminMenuLanguage.objects.all().delete()

        menu = []

        # tuple structure
        # model name or applabel:modelname, label, icon, url, prefix, active_all, active groups, submenu

        try:
            from prjcore.settings import custom_dwadmin_menu
        except ImportError:
            pass
        else:
            menu = custom_dwadmin_menu(menu_config=menu, debug=debug)

        create_menu(None, menu, debug)

        self.stdout.write("creation finished")
