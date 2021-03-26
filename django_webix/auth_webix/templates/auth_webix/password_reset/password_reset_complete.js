{% load static %}

{% block webix_content %}
    webix.ui([], $$("{{ webix_container_id }}"));

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
                    {% block password_reset_instructions %}
                        {
                            view: "template",
                            template: "La tua password è stata impostata. Ora puoi effettuare l'accesso.",
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_back %}
                        {
                            view: "form",
                            borderless: true,
                            elements: [
                                {
                                    view: "button", value: "Accedi", click: function () {
                                        location.href = "{{ login_url }}";
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
{% endblock %}
