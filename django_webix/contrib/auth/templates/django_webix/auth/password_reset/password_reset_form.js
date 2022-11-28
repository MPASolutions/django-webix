{% load static %}

{% block webix_content %}
    webix.ui([], $$("{{ webix_container_id }}"));

    {# Errors #}
    {% include "django_webix/include/form_errors_server.js" %}
    {% if is_errors_on_popup %}
        {% include "django_webix/include/form_errors_popup.js" %}
    {% else %}
        {% include "django_webix/include/form_errors_message.js" %}
    {% endif %}


    $$("{{ webix_container_id }}").addView({
        cols: [
            {$template: "Spacer"},
            {
                rows: [
                    {$template: "Spacer"},
                    {% block content_extra_top %}{% endblock %}
                    {% block password_reset_title %}
                        {
                            view: "template",
                            minWidth: 500,
                            template: "<h2>{{ title }}</h2>",
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_instructions %}
                        {
                            view: "template",
                            template: '{{ _("Forgot password? Enter your email address below, and we will send you instructions to set up a new one")|escapejs }}',
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {
                        view: "form",
                        borderless: true,
                        id: "{{ form.webix_id }}",
                        minWidth: 500,
                        elements: [
                            {{ form.as_webix|safe }},

                            {# Buttons #}
                            {
                                cols: [
                                    {
                                        view: "button",
                                        value: "{{ _("Reset my password")|escapejs }}",
                                        type: "form",
                                        click: function () {
                                            {% include "django_webix/include/toolbar_form_save.js"%}
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {% block password_reset_back %}
                        {
                            view: "form",
                            borderless: true,
                            elements: [
                                {
                                    view: "button",
                                    css: "webix_transparent",
                                    value: "{{ _("Go back to the home page")|escapejs }}",
                                    click: function () {
                                        location.href = "/";
                                    }
                                }
                            ]
                        },
                    {% endblock %}
                    {% block content_extra_bottom %}{% endblock %}
                    {$template: "Spacer"}
                ]
            },
            {$template: "Spacer"}
        ]
    });

    {% include "django_webix/include/toolbar_form_validate.js" %}
{% endblock %}
