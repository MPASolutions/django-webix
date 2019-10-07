{% load django_webix_utils %}

$$("{{ webix_container_id }}").addView({
    id: "header_failure_related_objects",
    view: "template",
    template: "Mancano dei dati per poter aggiungere dati",
    type: "header",
});

$$("{{ webix_container_id }}").addView({
    height:70,
});

{% for el in failure_add_missing_objects %}
    $$("{{ webix_container_id }}").addView({
        id: "button_{{ forloop.counter }}",
        view: "button",
        value: "{{ el.text }}",
        css: 'failure_add_missing_objects',
        height: 50,
        padding: 10,
        margin: 2,
        click: function () {
            load_js("{{ el.url }}");
        }
    });
{% endfor %}
