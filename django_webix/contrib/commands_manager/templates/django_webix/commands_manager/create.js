{% extends 'django_webix/generic/update.js' %}

{% block webix_content %}
{{ block.super }}

{% include "django_webix/commands_manager/common.js" %}
{% endblock %}
