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
                            template: "Abbiamo inviato istruzioni per impostare la password all'indirizzo email che hai indicato. Dovresti riceverle a breve a patto che l'indirizzo che hai inserito sia valido.",
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_spam %}
                        {
                            view: "template",
                            template: "Se non ricevi un messaggio email, accertati di aver inserito l'indirizzo con cui ti sei registrato, e controlla la cartella dello spam.",
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
{% endblock %}
