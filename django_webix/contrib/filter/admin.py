from django.contrib import admin
from django.contrib.admin import register

from django_webix.contrib.filter.models import WebixFilter


@register(WebixFilter)
class WebixFilterAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "model", "insert_user", "visibility"]
    search_fields = ["title", "description", "model", "insert_user__username", "visibility"]
    list_filter = ["model", "visibility"]
