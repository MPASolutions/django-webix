URLs
====

django-webix views use a URL naming convention to automatically resolve links between list, create,
update, and delete views. Following this convention means the views can generate navigation URLs
(breadcrumbs, buttons, redirects) without any manual configuration.


URL Naming Convention
---------------------

The default pattern is ``<app_label>.<model_name>.<action>``:

.. code-block:: text

    myapp.product.list
    myapp.product.create
    myapp.product.update
    myapp.product.delete

This is derived from the model's ``app_label`` and ``model_name`` (from ``Meta``). The view resolves
these patterns using ``WebixUrlMixin.get_model_name()``:

.. code-block:: python

    # Default: "myapp.product"
    def get_model_name(self):
        return "{}.{}".format(
            self.model._meta.app_label,
            self.model._meta.model_name
        )


Complete CRUD URL Pattern
-------------------------

Register all four views for a model:

.. code-block:: python

    from django.urls import path
    from myapp.views import (
        ProductListView,
        ProductCreateView,
        ProductUpdateView,
        ProductDeleteView,
    )

    urlpatterns = [
        path('products/', ProductListView.as_view(), name='myapp.product.list'),
        path('products/create/', ProductCreateView.as_view(), name='myapp.product.create'),
        path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='myapp.product.update'),
        path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='myapp.product.delete'),
    ]

The update and delete views require an ``<int:pk>`` URL parameter.


URL Attributes in Views
-----------------------

Override these attributes on a view to use custom URL pattern names instead of the auto-generated ones:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Attribute
     - Default
     - Description
   * - ``url_pattern_list``
     - ``None``
     - Custom URL name for the list view. Defaults to ``<app_label>.<model_name>.list``.
   * - ``url_pattern_create``
     - ``None``
     - Custom URL name for the create view.
   * - ``url_pattern_update``
     - ``None``
     - Custom URL name for the update view.
   * - ``url_pattern_delete``
     - ``None``
     - Custom URL name for the delete view.
   * - ``url_using_namespace``
     - ``False``
     - If ``True``, use ``:`` as separator (namespaced URLs) instead of ``.``.
       E.g., ``myapp:product.list`` instead of ``myapp.product.list``.

**Example with custom URL patterns:**

.. code-block:: python

    class ProductListView(WebixListView):
        model = Product
        url_pattern_list = 'inventory.products.list'
        url_pattern_create = 'inventory.products.new'
        url_pattern_update = 'inventory.products.edit'
        url_pattern_delete = 'inventory.products.remove'

**Example with namespaced URLs:**

.. code-block:: python

    # urls.py
    app_name = 'inventory'
    urlpatterns = [
        path('products/', ProductListView.as_view(), name='product.list'),
        path('products/create/', ProductCreateView.as_view(), name='product.create'),
        path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product.update'),
        path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product.delete'),
    ]

    # views.py
    class ProductListView(WebixListView):
        model = Product
        url_using_namespace = True  # resolves "inventory:product.list"


URL Helper Methods
------------------

``WebixUrlMixin`` provides methods to generate resolved URLs. These are available in all views:

.. code-block:: python

    self.get_url_list()              # e.g., '/products/'
    self.get_url_create()            # e.g., '/products/create/'
    self.get_url_update(obj=self.object)  # e.g., '/products/5/update/'
    self.get_url_delete(obj=self.object)  # e.g., '/products/5/delete/'

These methods return ``None`` if the URL pattern does not exist (i.e., the corresponding view is
not registered). The templates use this to conditionally show/hide navigation buttons.


Including django-webix URLs
---------------------------

Add the django-webix base URLs to your project (for autocomplete and internal views):

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        # ...
        path('django-webix/', include('django_webix.urls')),
        # ...
    ]


Conditional URL Registration
-----------------------------

Conditionally register URLs based on installed apps:

.. code-block:: python

    from django.apps import apps
    from django.urls import path, include

    urlpatterns = [
        path('django-webix/', include('django_webix.urls')),
    ]

    if apps.is_installed('myapp'):
        from myapp.views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView
        urlpatterns += [
            path('products/', ProductListView.as_view(), name='myapp.product.list'),
            path('products/create/', ProductCreateView.as_view(), name='myapp.product.create'),
            path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='myapp.product.update'),
            path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='myapp.product.delete'),
        ]


Admin URL Registration
----------------------

When using ``django_webix.contrib.admin``, URLs are auto-generated based on the registered models.
See the :doc:`/contrib/admin/basic_usage` documentation for details.
