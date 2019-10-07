.. :changelog:

.. _KeepAChangelog: http://keepachangelog.com/
.. _SemanticVersioning: http://semver.org/

Change Log
----------

All notable changes to this project will be documented in this file.

The format is based on KeepAChangelog_ and this project adheres to SemanticVersioning_.

[Unreleased]
++++++++++++

Added
~~~~~
* `WebixUrlMixin` parent class of all django-webix views
* Set `permissions` into django-webix views to use django permissions (default True: use django permissions)
* Set `logs` into django-webix views to use django log entries
* `style` variable in `WebixCreateView` `WebixUpdateView` with possible values: `merged` and `unmerged`
* Added all permission types in context of all django-webix views
* Added urls in context of all django-webix views
* Added `model` and `model_name` in context of all django-webix views

Changed
~~~~~~~
* `get_model_name`, `get_url_list`, `get_url_create`, `get_url_update`, `get_url_delete` moved to `WebixUrlMixin` as methods
* Changed permissions check in templates

Removed
~~~~~~~
* Removed `get_model_name` from `GenericModelWebix`
* Removed `get_url_list` from `GenericModelWebix`
* Removed `get_url_create` from `GenericModelWebix`
* Removed `get_url_update` from `GenericModelWebix`
* Removed `get_url_delete` from `GenericModelWebix`

Fixed
~~~~~
* Check if `django.contrib.admin` is installed before add log entry

Deprecated
~~~~~~~~~~
* `GenericModelWebix` will be removed in a future release
* `WebixCreateWithInlinesView` has been renamed to `WebixCreateView`
* `WebixCreateWithInlinesUnmergedView` has been renamed to `WebixCreateView`
* `WebixUpdateWithInlinesView` has been renamed to `WebixUpdateView`
* `WebixUpdateWithInlinesUnmergedView` has been renamed to `WebixUpdateView`


[0.2.2] - 2019-08-06
++++++++++++++++++++

Added
~~~~~
* Tree of nested object before delete an instance
* Prevent to delete an instance if has at least one nested object

Changed
~~~~~~~
* Django-extra-view updates
* `get_model_name` change separator between app_label and model_name from `_` to `.`

Fixed
~~~~~
* Add new line in inline forms with filefield


[0.2.1] - 2019-08-05
++++++++++++++++++++

Added
~~~~~
* Compatibility with Django 2.2

Changed
~~~~~~~
* Renamed templatetag `utils_getattr` to `django_webix_utils`

Fixed
~~~~~
* FileField download button
* FileField autoWidth
* Create new inline from empty form


[0.2.0] - 2019-02-26
++++++++++++++++++++

Added
~~~~~
* Compatibility with Webix 6
* Added RadioSelect widget
* Added empty choice in select widget
* Form fields type checked with isinstance method

Changed
~~~~~~~
* Changed static path


[0.1.5] - 2018-10-11
++++++++++++++++++++

Added
~~~~~
* JSONField postgresql support

Fixed
~~~~~
* Fix empty form fields initial values on clean validation error


[0.1.4] - 2018-10-02
++++++++++++++++++++

Fixed
~~~~~
* Fix delete button click ajax data


[0.1.3] - 2018-10-01
++++++++++++++++++++

Changed
~~~~~~~
* Hide tabbar without inlines

Fixed
~~~~~
* Fix readonly dates


[0.1.2] - 2018-10-01
++++++++++++++++++++

Changed
~~~~~~~
* Static files updates and include fixes


[0.1.1] - 2018-09-26
++++++++++++++++++++

Fixed
~~~~~
* Serializer encoder fix


[0.1] - 2018-09-26
++++++++++++++++++

Added
~~~~~
* First release on PyPI.
