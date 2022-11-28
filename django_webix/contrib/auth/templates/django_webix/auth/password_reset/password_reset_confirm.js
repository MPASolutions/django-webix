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
                            template: "<h2>{{ title }}</h2>",
                            minWidth: 500,
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% if validlink %}
                        {% block password_reset_instructions %}
                            {
                                view: "template",
                                template: "{{ _("Enter the new password twice, to verify that you have written it correctly")|escapejs }}",
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
                                            value: "{{ _("Change my password")|escapejs }}",
                                            type: "form",
                                            click: function () {
                                                {% include "django_webix/include/toolbar_form_save.js"%}
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                    {% else %}
                        {% block password_reset_instructions_invalid %}
                            {
                                view: "template",
                                template: "{{ _("The link you used is invalid, try to request a new email to reset your password.")|escapejs }}",
                                autoheight: true,
                                borderless: true,
                                css: {"text-align": 'center'}
                            },
                        {% endblock %}
                    {% endif %}
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

    $$('{{ form.webix_id }}').setValues({csrfmiddlewaretoken: "{{ csrf_token }}"});

    {% include "django_webix/include/toolbar_form_validate.js" %}
{% endblock %}
