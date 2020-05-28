Class Reference
===============

Decorators
----------
.. autofunction:: django_webix.views.generic.decorators.action_config
.. autofunction:: django_webix.utils.decorators.script_login_required

Template Tags
-------------
.. automodule:: django_webix.templatetags.django_webix_utils
   :members:

Forms
-----
.. autoclass:: django_webix.forms.forms.BaseWebixForm
    :members:
.. autoclass:: django_webix.forms.forms.BaseWebixModelForm
    :members:
.. autoclass:: django_webix.forms.WebixForm
    :members:
.. autoclass:: django_webix.forms.WebixModelForm
    :members:

Forms Mixin
-----------
.. autoclass:: django_webix.forms.forms.BaseWebixMixin
    :members:

Formsets
--------
.. autoclass:: django_webix.forms.formsets.WebixManagementForm
    :members:
.. autoclass:: django_webix.forms.formsets.BaseWebixInlineFormSet
    :members:
.. autoclass:: django_webix.forms.formsets.WebixInlineFormSet
    :members:
.. autoclass:: django_webix.forms.formsets.WebixStackedInlineFormSet
    :members:
.. autoclass:: django_webix.forms.formsets.WebixTabularInlineFormSet
    :members:

Views
-----
.. autoclass:: django_webix.views.WebixListView
    :members:
.. autoclass:: django_webix.views.WebixDetailView
    :members:
.. autoclass:: django_webix.views.WebixCreateView
    :members:
.. autoclass:: django_webix.views.WebixUpdateView
    :members:
.. autoclass:: django_webix.views.WebixDeleteView
    :members:
.. autoclass:: django_webix.views.WebixTemplateView
    :members:
.. autoclass:: django_webix.views.WebixTemplateListView
    :members:

View Mixins
-----------
.. autoclass:: django_webix.views.generic.base.WebixPermissionsMixin
    :members:
.. autoclass:: django_webix.views.generic.base.WebixUrlMixin
    :members:
.. autoclass:: django_webix.views.generic.base.WebixBaseMixin
    :members:
.. autoclass:: django_webix.views.generic.create_update.WebixCreateUpdateMixin
    :members:

Utils
-----
.. autofunction:: django_webix.utils.filters.from_dict_to_qset

Admin Config
------------
.. autoclass:: django_webix.admin_webix.apps.SimpleAdminWebixConfig
    :members:
.. autoclass:: django_webix.admin_webix.apps.AdminWebixConfig
    :members:

Admin Decorators
----------------
.. autofunction:: django_webix.admin_webix.decorators.register

Admin Options
-------------
.. autoclass:: django_webix.admin_webix.options.ModelWebixAdmin
    :members:

Admin Sites
-----------
.. autoclass:: django_webix.admin_webix.sites.AlreadyRegistered
    :members:
.. autoclass:: django_webix.admin_webix.sites.NotRegistered
    :members:
.. autoclass:: django_webix.admin_webix.sites.AdminWebixSite
    :members:
.. autoclass:: django_webix.admin_webix.sites.DefaultAdminWebixSite
    :members:
