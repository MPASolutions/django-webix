import datetime

from django.db.models import F, Q
from django_webix.views import WebixListView as ListView
from django_webix.contrib.tutorial.models import TutorialItem

from django.utils.html import escapejs
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

class TutorialListView(ListView):
    model = TutorialItem
    template_name = 'django_webix/tutorial/list.js'
    title = _("Video instructions and manuals")
    order_by = ['name']

    enable_column_copy = False
    enable_column_delete = False
    enable_row_click = False
    enable_actions = False

    add_permission = False
    change_permission = False
    delete_permission = False

    def get_fields(self):
        _fields = [
            {
                'field_name': 'icon',
                'datalist_column': '''{
                    id: "icon",
                    header: [""],
                    width: 40,
                    template: typeIcon
                }'''
            },
            {
                'field_name': 'name',
                'datalist_column': format_lazy(
                    '''{{
                        id: "name",
                        header: ["{}"],
                        fillspace: true
                    }}''',
                    escapejs(_("Name")))
            },
            {
                'field_name': 'description',
                'datalist_column': format_lazy(
                    '''{{
                    id: "description",
                    header: ["{}"],
                    fillspace: true
                    }}''',
                    escapejs(_("Description")))
            },
            {
                'field_name': 'url',
                'datalist_column': '''{
                    id: "url",
                    hidden: true,
                    headermenu: false
                }'''
            },
            {
                'field_name': 'tutorial_type',
                'datalist_column': '''{
                    id: "tutorial_type",
                    hidden: true,
                    headermenu: false
                }'''
            },
            {
                'field_name': 'target',
                'datalist_column': '''{
                    id: "target",
                    hidden: true,
                    headermenu: false
                }'''
            }
        ]
        return super().get_fields(fields = _fields)


    def get_queryset(self, initial_queryset=None):
        queryset = super(TutorialListView, self).get_queryset(initial_queryset=initial_queryset)

        # Icon
        queryset = queryset.annotate(icon=F('tutorial_type'))

        # validiy filter
        queryset = queryset.filter(
            Q(visible_from__isnull=True) | Q(visible_from__lte=datetime.date.today()),
            Q(visible_to__isnull=True) | Q(visible_to__gte=datetime.date.today()),
        )

        area = self.request.GET.get('area')
        if area is not None:
            queryset = queryset.filter(area__name=self.request.GET.get('area'))

        return queryset
