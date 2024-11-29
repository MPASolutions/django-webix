Urls
=====

Register the views url (e.g. <project_name>/urls.py)

.. code-block:: python

    from django.urls import path

    from <app_name>.views import HomeView, MyModelListView, MyModelCreateView, MyModelUpdateView, MyModelDeleteView

    urlpatterns = [
        # ...
        path('', HomeView.as_view(), name='home'),

        path('mymodel/list', MyModelListView.as_view(), name='myapplication.mymodel.list'),
        path('mymodel/create', MyModelCreateView.as_view(), name='myapplication.mymodel.create'),
        path('mymodel/update/<int:pk>', MyModelUpdateView.as_view(), name='myapplication.mymodel.update'),
        path('mymodel/delete/<int:pk>', MyModelDeleteView.as_view(), name='myapplication.mymodel.delete'),
        # ...
    ]
