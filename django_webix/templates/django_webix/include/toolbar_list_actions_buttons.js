{# bottoni singoli #}
var toolbar_actions = [];
$.each(actions_list, function (index, obj) {
    toolbar_actions.push({
        view: "tootipButton",
        autowidth: true,
        id: 'action_' + obj.id,
        value: '' + obj.value,
        click: function () {
            ids = [];
            $$("datatable_{{ model_name }}").eachRow(function (id) {
                if (this.getItem(id).checkbox_action) {
                    ids.push(id)
                }
            });
            if (ids.length > 0) {
                actions_execute(obj.id, ids);
            } else {
                webix.alert("Non è stata selezionata nessuna riga", "alert-warning");

            }

        }

    });
});
