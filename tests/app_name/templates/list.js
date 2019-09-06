webix.ui([], $$("{{ view.webix_view_id|default:"content_right" }}"));

$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    rows: [
        {
            id: '{{ object_list.model|get_model_name }}',
            view: "datatable",
            resizeColumn: true,
            data: {{ datalist|safe }},
            select: "row",
            columns: [
                {
                    id: "field",
                    header: "Field",
                    fillspace: true
                }
            ],
            on: {
                onItemDblClick: function (id, e, trg) {
                    var $this = this;

                    $.ajax({
                        url: '{% url 'app_name.mymodel.update' 1 %}'.replace('1', id.row),
                        dataType: "script",
                        success: function (text, data, XmlHttpRequest) {
                        },
                        error: function () {
                            alert('Error')
                        }
                    });
                }
            }
        },
        {
            view: "toolbar",
            id: "myToolbar",
            cols: [
                {
                    view: "button", value: "New", width: 100, align: "center", click: function () {
                        $.ajax({
                            url: '{% url 'app_name.mymodel.create' %}',
                            dataType: "script",
                            success: function (text, data, XmlHttpRequest) {
                            },
                            error: function () {
                                alert('Error')
                            }
                        });
                    }
                }
            ]
        }
    ]
}, -1);
