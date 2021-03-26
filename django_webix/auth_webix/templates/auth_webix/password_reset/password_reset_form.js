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
                            template: "Password dimenticata? Inserisci il tuo indirizzo email qui sotto, e ti invieremo istruzioni per impostarne una nuova.",
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
                                        value: "Reimposta la mia password",
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

    {% include "django_webix/include/toolbar_form_validate.js" %}
{% endblock %}
