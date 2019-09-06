{% load django_webix_utils %}

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {% if url_back and url_back != '' %}
        {
            view: "button",
            type: "base",
            align: "left",
            label: "Torna indietro",
            autowidth: true,
            click: function () {
                load_js("{{url_back}}");
            }
        },
        {% elif not url_list or url_list != '' %}
        {
            view: "button",
            type: "base",
            align: "left",
            label: "Torna alla lista",
            autowidth: true,
            click: function () {
                load_js("{% url url_list %}");
            }
        },
        {% endif %}
        {
            view: "template",
            type: "header",
            template: '<p style="text-align:center;">{% if object %}{{model|getattr:"_meta"|getattr:"verbose_name"}}: {{object}}{% else %}Aggiungi {{model|getattr:"_meta"|getattr:"verbose_name"}} {% endif %}</p>',
        }
    ]
});
