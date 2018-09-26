{% load utils_getattr %}

{% if related %}

var datalist = [
    {% for el in related %}
    [
        "{{el.pk}}",
        "{{el|getattr:"_meta"|getattr:"verbose_name"}}",
        "{{el}}",
        {% if not disable_link_related %}
        "{% url el.get_url_update el.pk %}"
        {% endif %}
    ]{% if not forloop.last %}, {% endif %}
    {% endfor %}
]

$$("{{view.webix_view_id|default:"content_right"}}").addView(
    {
        'view': "template",
        'template': "Non puoi cancellare questo elemento se prima non hai eliminato le seguenti schede:",
        'type': "header",
        'css': 'webix_error'
    }
);

$$("{{view.webix_view_id|default:"content_right"}}").addView({
    // multiselect: true,
    multiselect: "touch",
    id: 'list_deleting',
    view: "datatable",
    columns: [
        {id: "data1", header: "Tipo di dato", adjust: "all"},
        {id: "data2", header: ["Denominazione", {content: "textFilter"}], fillspace: true},
    ],
    datatype: "jsarray",
    data: webix.copy(datalist),
    navigation: true,
    select: "row",
    {% if not disable_link_related %}
    on: {
        onItemClick: function (id, e, trg) {
            var el = $$('list_deleting').getSelectedItem();
            load_js(el['data3']);
        }
    },
    {% endif %}
});
$$("{{view.webix_view_id|default:"content_right"}}").addView(
    {
        view: "toolbar", margin: 5, cols: [
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: "Torna alla lista",
                width: 150,
                click: function () {
                    load_js("{% url object.get_url_list %}");
                }
            },
            {$template: "Spacer"},

        ]
    }, -1);

{% endif %}
