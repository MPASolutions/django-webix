{# counter #}
function update_counter() {
    ids = [];
    $$("datatable_{{ model_name }}").eachRow(function (id) {
        if ((this.getItem(id)!=undefined )&&( this.getItem(id).checkbox_action)) {
            ids.push(id)
        }
    });
    if (ids.length > 0) {
        txt = ids.length + ' di ' + $$('datatable_{{ model_name }}').count() + ' elementi';
    } else {
        txt = $$('datatable_{{ model_name }}').count() + ' elementi';
    }
    $$('stats_list').define('label', txt);
    $$('stats_list').refresh();
}

{# hide column selection if no one actions #}
if ((typeof actions_list == 'undefined') || (typeof actions_execute == 'undefined') || (actions_list.length == 0)) {
    $$('datatable_{{ model_name }}').hideColumn("checkbox_action");
    var toolbar_actions = [];
}

{% block toolbar_list_actions %}
    {% if actions_style == 'buttons' %}
        {% include "django_webix/include/toolbar_list_actions_buttons.js" %}
    {% endif %}
    {% if actions_style == 'select' %}
        {% include "django_webix/include/toolbar_list_actions_select.js" %}
    {% endif %}
{% endblock %}

{# create toolbar footer #}
$$("{{webix_container_id}}").addView({
    view: "toolbar",
    margin: 5,
    height: 65,
    cols: toolbar_actions.concat([
        {id: 'stats_list', view: 'label', label: '', width: 170},

        {% block toolbar_middle %}
        {$template: "Spacer"},
        {% endblock %}

        {% block add_button %}
        {% if has_add_permission or not remove_disabled_buttons and not has_add_permission %}
        {
            view: "tootipButton",
            type: "form",
            align: "right",
            label: 'Aggiungi nuovo',
            {% if not has_add_permission %}
            disabled: true,
            tooltip: '{{ info_no_add_permission|join:", " }}',
            {% endif %}
            width: 150,
            click: function () {
                load_js('{{ url_create }}')
            }
        }
        {% endif %}
        {% endblock %}
    ])
});
update_counter();
$$("datatable_{{ model_name }}").attachEvent("onCheck", function (row, column, state) {
    update_counter()
});
