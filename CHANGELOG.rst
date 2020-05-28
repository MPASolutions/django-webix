.. :changelog:

.. _KeepAChangelog: http://keepachangelog.com/
.. _SemanticVersioning: http://semver.org/

Change Log
----------

All notable changes to this project will be documented in this file.

The format is based on KeepAChangelog_ and this project adheres to SemanticVersioning_.

[Unreleased]
++++++++++++


[1.2.1] 2020-01-08
++++++++++++++++++

Changed
~~~~~~~
* Documentation


[1.2.0] 2020-05-28
++++++++++++++++++

Added
~~~~~
* Added `admin` subpackage
* Added auto localizated fields
* Added new translations
* Added `delete` confirmation message
* Added extra title for `WebixUpdateView`
* Added overlay container in settings with default `webix_container_id`
* Added signal in each view when some instance change
* Added name for toolbar
* Added `delete` action on list
* Added paging on list
* Added settings to set url of `fontawesome`
* Added param to allows different `dataType` with `load_js`
* Added option to specify which nested models will be show on delete page
* Added string fields config on `WebixListView` by default
* Added default `abort` for all base ajax requests
* Added `decorator` for identify user not authenticated and popup to login
* Added pk field option if `pk_field` different from 'id'
* Added `ordering` into `get_queryset` for standard generic views

Changed
~~~~~~~
* `InlineForeignKey` separated from control
* Split utils into multiple file
* Changed prefix in `WebixListView` templates
* Add extra ajax params to `load_js` function
* Header borderless

Removed
~~~~~~~
* remove empy choices

Fixed
~~~~~
* Fixed `SimpleArrayField` initial
* Fixed `DateField` initial
* Fixed `delete` and `copy` functions
* Fixed translations and adjust indentations
* Fixed inline stacked js
* Fixed list queryset
* Fixed post delete valid
* Fixed list without actions and list ordering
* Fixed upload label background
* Fixed delete action
* Fixed list without fields
* Fixed `get_url_create` with kwargs
* Fixed tag trans with escapejs
* Fixed choice for action style type
* Fixed autocomplete fix IE11
* Fixed `WebixListView` with paging and without
* Fixed url on is_popup
* Fixed `WebixListView` and `WebixTemplateView` without model
* Fixed `delete` and `copy` columns
* Fixed function before send expecially for csrf
* Fixed form send custom widget


[1.1.0] 2020-01-08
++++++++++++++++++

Added
~~~~~
* Added kwargs params on create for reverse url
* Added header inlines option
* Added post with parameters for redirect
* Added create and delete permission on formsets
* Added `ArrayField` of date on forms
* Added multiple file support
* Added option to put inline not in standard place
* Added webix `overlay` container id
* Added `geometry field` hidden
* Added initial by post on add

Changed
~~~~~~~
* Better button for add row on inlines

Removed
~~~~~~~
* Removed console.log

Fixed
~~~~~
* Fixed toolbar extra params
* Fixed template toolbar nav
* Fixed create/update template style
* Fixed stacked inline without rows
* Fixed delete button
* Fixed inline id
* Fixed readonly and autocomplete for inlines
* Fixed autocomplete fields
* Fixed default function post save form before inlines
* Fixed post form save before save inlines on update
* Fixed overlay only if exists
* Fixed `BaseWebixModelForm` with Django <= 2.0
* Fixed `FileField`
* Fixed import geos
* Fixed `InlineForeignKeyField`
* Fixed file input
* Fixed toolbar navigation escapejs


[1.0.0] 2019-10-07
++++++++++++++++++

Added
~~~~~
* Added translations
* `WebixUrlMixin` parent class of all django-webix views
* Set `permissions` into django-webix views to use django permissions (default True: use django permissions)
* Set `logs` into django-webix views to use django log entries
* `style` variable in `WebixCreateView` `WebixUpdateView` with possible values: `merged` and `unmerged`
* Added all permission types in context of all django-webix views
* Added urls in context of all django-webix views
* Added `model` and `model_name` in context of all django-webix views
* Added `CreateUpdateMixin`
* Added hedermenu, generic title, excel datatable webix export
* Added `TemplateListView` class view
* Added inline_id into inline forms and hook for custom js function for each inline
* Added true to checkbox boolean field
* Added disabled list actions
* Added `django_type_field` to identify original formfield
* Added model unique together validation into generic views

Changed
~~~~~~~
* `get_model_name`, `get_url_list`, `get_url_create`, `get_url_update`, `get_url_delete` moved to `WebixUrlMixin` as methods
* Changed permissions check in templates
* Separated generic views
* Improve copy list function

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
* Tests postgres database name
* Init `WebixModelForm` and `BaseWebixMixin` fix
* Forms `clean` method fix
* Fixed delete get_failure_delete_related_objects method
* Fixed initial values for inlines
* Fixed `JSONField`

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
