{% load django_webix_utils %}

{% if url_list and url_list != '' %}
    $$("{{ view.webix_view_id|default:"content_right" }}").addView({
        id: 'main_toolbar_navigation',
        view: "toolbar",
        margin: 5,
        cols: [
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: 'Torna alla lista "{{ form.instance|getattr:"_meta"|getattr:"verbose_name_plural" }}"',
                autowidth: true,
                click: function () {
                    load_js("{% url url_list %}");
                }
            }
        ]
    });
{% endif %}
