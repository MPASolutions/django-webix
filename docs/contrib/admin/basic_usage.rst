Admin Base
==========

Install dependencies
--------------------

.. code-block::

    $ python -m pip install django-webix[admin]


Admin Webix Site
----------------

Use base admin site.

.. code-block:: python

    from django_webix import dwadmin as admin

Admin Webix Model registration
------------------------------

Create the files (e.g. <app_name>/dwadmin.py)
- prefix could be used for multiple model registration
Here an example:

.. code-block:: python

    from <app_name>.models import ModelName
    from django_webix import dwadmin as admin

    @admin.register(Conferente, prefix=prefix)
    class ConferenteAdmin(admin.ModelWebixAdmin):

        list_display = ['field_1', 'field_2']
        enable_json_loading = True
