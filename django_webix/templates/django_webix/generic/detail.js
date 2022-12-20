{% load django_webix_utils i18n %}

{% block main_content %}
    {% if failure_view_blocking_objects %}
        {% block failure_blocking_objects %}
            {% include "django_webix/include/list_failure_blocking_objects.js"  with failure_blocking_objects=failure_view_blocking_objects %}
        {% endblock %}
    {% else %}
        {% if failure_view_related_objects %}
            {% block failure_related_objects %}
                {% include "django_webix/include/list_failure_related_objects.js" with failure_related_objects=failure_view_related_objects %}
            {% endblock %}
        {% else %}
            {% block content %}
                {# TODO #}
            {% endblock %}
        {% endif %}
    {% endif %}
{% endblock %}
