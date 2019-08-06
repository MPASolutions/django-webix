.. :changelog:

.. _KeepAChangelog: http://keepachangelog.com/
.. _SemanticVersioning: http://semver.org/

Change Log
----------

All notable changes to this project will be documented in this file.

The format is based on KeepAChangelog_ and this project adheres to SemanticVersioning_.

[Unreleased]
++++++++++++


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
