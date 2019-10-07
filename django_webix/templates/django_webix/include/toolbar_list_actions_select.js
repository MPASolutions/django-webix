{# actions su select #}
if ((typeof actions_list != 'undefined') && (typeof actions_execute != 'undefined') && (actions_list.length > 0)) {
    var toolbar_actions = [
        {
            view: "richselect",
            id: "action_combo",
            maxWidth: "300",
            minWidth: "200",
            width: "300",
            value: 1,
            labelWidth: 0,
            placeholder: "Seleziona una funzionalità ...",
            options: actions_list
        },
        {
            view: "tootipButton",
            id: "action_button",
            value: "Esegui",
            inputWidth: 60,
            width: 60,
            on: {
                onItemClick: function () {
                    var action = $$("action_combo").getValue();
                    ids = [];
                    $$("datatable_{{ model_name }}").eachRow(function (id) {
                        if ((this.getItem(id)!=undefined )&&( this.getItem(id).checkbox_action)) {
                            ids.push(id)
                        }
                    })
                    if (ids.length > 0) {
                        actions_execute(action, ids);
                    } else {
                        webix.alert("Non è stata selezionata nessuna riga", "alert-warning");
                    }

                }
            }
        }
    ]
}
