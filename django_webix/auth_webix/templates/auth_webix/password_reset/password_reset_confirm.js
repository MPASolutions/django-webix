{% load static %}

{% block webix_content %}
    webix.ui([], $$("{{ webix_container_id }}"));

    {# Errors #}
    {% if form.errors %}
        webix.message({type: "error", expire: 10000, text: "{{ form.errors|safe|escapejs }}"});
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
                                template: "Inserisci la nuova password due volte, per verificare di averla scritta correttamente.",
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
                                            value: "Modifica la mia password",
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
                                template: "Il link che hai utilizzato non è valido, prova a richiedere una nuova email per il reset della password.",
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
                                    value: "Torna alla pagina iniziale",
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
