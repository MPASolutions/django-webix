{% extends 'admin_webix/base_site.html' %}

{% load static %}
{% if is_app_installed %}
    {% load two_factor %}
{% endif %}

{% block extra_content %}
webix.ui([], $$("{{ webix_container_id }}"));

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>Reimposta la password</strong></div>'
        }
    ]
}, 0);


$$("{{ webix_container_id }}").addView({
    cols: [
        {},
        {
            rows: [
                {$template: "Spacer", height: 20},
                {
                    view: "template",
                    template: "Abbiamo inviato istruzioni per impostare la password all'indirizzo email che hai indicato. Dovresti riceverle a breve a patto che l'indirizzo che hai inserito sia valido.",
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {
                    view: "template",
                    template: "Se non ricevi un messaggio email, accertati di aver inserito l'indirizzo con cui ti sei registrato, e controlla la cartella dello spam.",
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {$template: "Spacer", height: 20},
            ]
        },
        {}
    ]
});


{% endblock %}
