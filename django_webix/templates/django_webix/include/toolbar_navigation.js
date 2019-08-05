{% load django_webix_utils %}

$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    height: 30,
    cols: [
        {% if form.instance.get_url_list != None and form.instance.get_url_list != '' %}
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: 'Torna alla lista "{{ form.instance|getattr:"_meta"|getattr:"verbose_name_plural" }}"',
                autowidth: true,
                click: function () {
                    load_js("{% url form.instance.get_url_list %}");
                }
            }
        {% endif %}
    ]
}, 0);
