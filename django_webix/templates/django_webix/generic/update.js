{% load django_webix_utils i18n %}

{% block webix_content %}

    {% block context_cleaner %}
        webix.ui([], $$("{{ webix_container_id }}"));
    {% endblock %}

    {% block toolbar_navigation %}
        {% include "django_webix/include/toolbar_navigation.js" %}
    {% endblock %}

    {% if failure_change_blocking_objects %}
        {% include "django_webix/include/list_failure_blocking_objects.js"  with failure_blocking_objects=failure_change_blocking_objects %}
    {% else %}
        {% if failure_change_related_objects %}
            {% block failure_related_objects %}
                {% include "django_webix/include/list_failure_related_objects.js" with failure_related_objects=failure_change_related_objects %}
            {% endblock %}
        {% else %}
            {% block form_standard %}
                {% if template_style == 'standard' %}
                    {% include "django_webix/include/form_standard.js" %}
                {% endif %}
                {% if template_style == 'tabs' %}
                    {% include "django_webix/include/form_tabs.js" %}
                {% endif %}
                {% if template_style == 'monotabs' %}
                    {% include "django_webix/include/form_monotabs.js" %}
                {% endif %}
            {% endblock %}
        {% endif %}

        {% block toolbar_form %}
            {% include "django_webix/include/toolbar_form.js" %}
        {% endblock %}

        {% block extrajs_post %}{% endblock %}
    {% endif %}

{% endblock %}
