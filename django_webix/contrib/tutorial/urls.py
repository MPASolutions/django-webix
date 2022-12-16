from django.urls import path

from django_webix.contrib.tutorial.views import TutorialListView

urlpatterns = [
    path("django-webix-tutorial/list", TutorialListView.as_view(), name='dwtutorial.tutorialitem.list')
]
