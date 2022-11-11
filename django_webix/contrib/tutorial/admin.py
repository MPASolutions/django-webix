
from django.contrib import admin
from django_webix_tutorial.models import TutorialArea, TutorialItem


@admin.register(TutorialArea)
class TutorialAreaAdmin(admin.ModelAdmin):
    pass


@admin.register(TutorialItem)
class TutorialItemAdmin(admin.ModelAdmin):
    pass
