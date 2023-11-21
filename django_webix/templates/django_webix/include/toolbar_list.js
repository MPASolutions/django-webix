{% load i18n %}

{# counter #}
function {{ view_prefix }}update_counter() {
    if ($$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox")!=undefined) {
        if ($$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox").isChecked() == false) {
            $$('{{ view_prefix }}select_all_checkbox').setValue(0);
        }
    }
    $$('{{ view_prefix }}select_all_button').hide();
    $$('{{ view_prefix }}unselect_all_button').hide();

    view_count = $$('{{ view_prefix }}datatable').view_count;
    view_count_total = $$('{{ view_prefix }}datatable').view_count_total;
    ids = [];
    $$("{{ view_prefix }}datatable").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id);
        }
    });
    if (ids.length != view_count) {
        $$('{{ view_prefix }}select_all_checkbox').setValue(0);
    } else {
        {% if not is_json_loading %}
            $$('{{ view_prefix }}select_all_checkbox').setValue(1);
        {% endif %}
    }
    if (ids.length > 0) {
        txt = ids.length + ' {{ _("of")|escapejs }} ' + view_count_total + ' {{ _("elements")|escapejs }}';
        {% if is_json_loading %}
            if (ids.length ==view_count) {
                if ($$('{{ view_prefix }}select_all_checkbox').getValue() == 0) {
                    $$('{{ view_prefix }}select_all_button').show();
                } else {
                    txt = '{{ _("All")|escapejs }} ' + view_count_total + ' {{ _("elements selected")|escapejs }}';
                    $$('{{ view_prefix }}unselect_all_button').show();
                }
            }
        {% else %}
            if ($$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox")!=undefined) {
                if ($$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox").isChecked() == true) {
                    txt = '{{ _("All")|escapejs }} ' + view_count_total + ' {{ _("elements selected")|escapejs }}';
                }
            }
        {% endif %}
    } else if (view_count_total != undefined) {
        txt = view_count_total + ' {{ _("elements")|escapejs }}';
    } else {
        txt = '';
    }

    $$('{{ view_prefix }}stats_list').define('label', txt);
    $$('{{ view_prefix }}stats_list').refresh();
}

function {{ view_prefix }}get_items_page_datatable() {
    ids = [];
    {% if is_json_loading %}
        per_page = {{ paginate_count_default }};
        page_number = $$("{{ view_prefix }}datatable").getPage();
        count_from = page_number * per_page;
        count_to = (page_number + 1) * per_page - 1;
        counter = 0;
        $$("{{ view_prefix }}datatable").eachRow(function (id) {
            if (counter >= count_from && counter <= count_to) {
                ids.push(id);
            }
            counter += 1;
        });
    {% else %}
        $$("{{ view_prefix }}datatable").eachRow(function (id) {
            ids.push(id);
        })
    {% endif %}
    return ids;
}

function {{ view_prefix }}prepare_actions_execute(action_name) {
    var ids = [];
    $$("{{ view_prefix }}datatable").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id);
        }
    })
    if (ids.length > 0) {
        var all = $$('{{ view_prefix }}select_all_checkbox').getValue()==1;
        {{ view_prefix }}actions_execute(action_name, ids, all);
    } else {
        webix.alert("{{_("No row has been selected")|escapejs}}", "alert-warning");
    }
}

{# hide column selection if no one actions #}
if ((typeof {{ view_prefix }}actions_list == 'undefined') || (typeof {{ view_prefix }}actions_execute == 'undefined') || ({{ view_prefix }}actions_list.length == 0)) {
    $$('{{ view_prefix }}datatable').hideColumn("checkbox_action");
    var {{ view_prefix }}toolbar_actions = [];
    var {{ view_prefix }}actions_list = [];
}

{% block toolbar_list_actions %}
{% include "django_webix/include/toolbar_list_actions.js" %}
{% endblock %}

{# create toolbar footer #}
$$("{{ webix_container_id }}").addView({
    view: "toolbar",
    margin: 5,
    id: "{{ webix_container_id }}_toolbar",
    {% if request.user_agent.is_mobile %}height:35,{% else %}height:55,{% endif %}
    cols: {{ view_prefix }}toolbar_actions.concat([
        {% block toolbar_middle %}
        {
            id: "{{ webix_container_id }}_toolbar_middle",
            cols: [{$template: "Spacer"}]
        },
        {% endblock %}

        {% block add_button %}
        {% if has_add_permission or not remove_disabled_buttons and not has_add_permission %}
        {
            id: "{{ view_prefix }}_addnew",
            view: "tootipButton",
            type: "form",
            align: "right",
            label: '{% if request.user_agent.is_mobile %}<div title="{{_("Add new")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-plus"></i></div>{% else %}{{_("Add new")|escapejs}}{% endif %}',
            {% if not has_add_permission %}
            disabled: true,
            tooltip: '{{ info_no_add_permission|join:", " }}',
            {% endif %}
            width: {% if request.user_agent.is_mobile %}40{% else %}150{% endif %},
            click: function () {
                load_js('{{ url_create|safe }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
            }
        }
        {% endif %}
        {% endblock %}
    ])
});

{{ view_prefix }}update_counter();
