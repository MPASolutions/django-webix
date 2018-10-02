$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    view: "form",
    id: "delete_form",
    cols: [{
        margin: 5,
        view: "toolbar",
        cols: [
            {
                view: "button",
                type: "base",
                align: "left",
                icon: "undo",
                label: 'Torna a "{{ object }}"',
                minWidth: 300,
                click: function () {
                    load_js("{% url object.get_url_update object.pk %}");
                }
            },
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
    }]
})
