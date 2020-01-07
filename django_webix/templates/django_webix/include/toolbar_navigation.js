{% load django_webix_utils %}

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {% if url_back and url_back != '' %}
        {
            view: "tootipButton",
            type: "base",
            align: "left",
            label: "Torna indietro",
            autowidth: true,
            click: function () {
                load_js("{{ url_back }}");
            }
        },
        {% elif url_list and url_list != '' %}
        {
            view: "tootipButton",
            type: "base",
            align: "left",
            label: "Torna alla lista",
            autowidth: true,
            click: function () {
                load_js("{{ url_list }}");
            }
        },
        {% endif %}
        {
            view: "template",
            type: "header",
            template: '<div style="width:100%; text-align:center;"><strong>{% if object %}{{ model|getattr:"_meta"|getattr:"verbose_name" }}: {{ object|escapejs }}{% else %}Aggiungi {{ model|getattr:"_meta"|getattr:"verbose_name" }}{% endif %}</strong></div>',
        }
    ]
}, 0);
