webix.ui([], $$("{{ view.webix_view_id|default:"content_right" }}"));

$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    height: 30,
    cols: [
        {% if object.get_url_update and object.get_url_update != '' %}
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: 'Torna a "{{ object }}"',
                autowidth: true,
                click: function () {
                    load_js("{% url object.get_url_update object.pk %}");
                }
            },
        {% elif object.get_url_list and object.get_url_list != '' %}
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: 'Torna a "{{ object }}"',
                autowidth: true,
                click: function () {
                  load_js("{% url object.get_url_list %}");
                }
            },
        {% endif %}
    ]
});

$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    view: "template",
    {% if nested_prevent %}
        template: "Non puoi cancellare questo elemento se prima non hai eliminato tutte le schede collegate",
    {% else %}
        template: "Le seguenti schede verranno eliminate",
    {% endif %}
    type: "header",
    css: 'webix_error'
});

$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    view: "tree",
    data: JSON.parse("{{ related|safe|escapejs }}"),
    on: {
        onItemClick: function(id, e, node) {
            var item = this.getItem(id);
            if ('url' in item) {
                load_js(item.url);
            }
        }
    }
});

{% if not nested_prevent and object.get_url_delete and object.get_url_delete != '' %}
    $$("{{ view.webix_view_id|default:"content_right" }}").addView({
        margin: 5,
        height: 30,
        view: "toolbar",
        cols: [
            {$template: "Spacer"},
            {
                view: "button",
                type: "form",
                align: "right",
                id: "delete",
                icon: "eraser",
                label: "Conferma cancellazione",
                width: 200,
                click: function () {
                    $.ajax({
                        url: "{% url object.get_url_delete object.pk %}",
                        dataType: "script",
                        type: "POST",
                        success: function () {
                            webix.ui.resize()
                        }
                    });
                }
            }
        ]
    });
{% endif %}

