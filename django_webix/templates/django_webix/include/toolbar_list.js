{% load i18n %}

{# counter #}
function update_counter() {
    view_count = $$('datatable_{{ model_name }}').view_count;
    view_count_total = $$('datatable_{{ model_name }}').view_count_total;
    ids = [];
    $$("datatable_{{ model_name }}").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id)
        }
    });
    if (ids.length!=view_count){
        $('input[name="master_checkbox"]').prop("checked",false) ;
        $$('select_all_checkbox').setValue(0);
    } else {
        $('input[name="master_checkbox"]').prop("checked",true) ;
        {% if not is_json_loading %}
        $$('select_all_checkbox').setValue(1);
        {% endif %}
    }
    if (ids.length > 0) {
        txt = ids.length + ' {{_("of")|escapejs}} ' + view_count_total + ' {{_("elements")|escapejs}}';
        {% if is_json_loading %}
        if (ids.length ==view_count) {
            if ($$('select_all_checkbox').getValue() == 0) {
                txt += '<div style="width:110px;float:right;height:100%;" class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Select all")|escapejs}}" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="$$(\'select_all_checkbox\').setValue(1);update_counter()"> {{_("Select all")|escapejs}} </button></div></div>';
            } else {
                txt = '{{_("All"|escapejs}} ' + view_count_total + ' {{_("elements selected")|escapejs}}';
                txt += '<div style="width:110px;float:right;height:100%;" class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Cancel selection")|escapejs}}" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="$$(\'select_all_checkbox\').setValue(0);$(\'input[name=master_checkbox]\').prop(\'checked\',false);master_checkbox_click();update_counter()"> {{_("Cancel selection")|escapejs}} </button></div></div>';
            }
        }
        {% else %}
        if ($('input[name="master_checkbox"]').prop("checked") == true) {
            txt = '{{_("All")|escapejs}} ' + view_count_total + ' {{_("elements selected")|escapejs}}';
        }

        {% endif %}
    } else if (view_count_total!=undefined) {
        txt = view_count_total + ' {{_("elements")|escapejs}}';
    } else {
        txt = '';
    }

    $$('stats_list').define('label', txt);
    $$('stats_list').refresh();
}

function get_items_page_datatable() {
    ids = [];
    {% if is_json_loading %}
    per_page = {{ paginate_count_default }};
    page_number = $$("datatable_{{ model_name }}").getPage();
    count_from = page_number * per_page;
    count_to = (page_number + 1) * per_page - 1;
    counter = 0;
    $$("datatable_{{ model_name }}").eachRow(function (id) {
        if (counter >= count_from && counter <= count_to) {
            ids.push(id)
        }
        counter += 1;
    });
    {% else %}
    $$("datatable_{{ model_name }}").eachRow(function (id) {
        ids.push(id)
        })
    {% endif %}
    return ids;
}


function master_checkbox_click() {
    $$('select_all_checkbox').setValue(0);
    if ($('input[name="master_checkbox"]').prop("checked") == true) {
        ids = get_items_page_datatable()
        $.each(ids, function (index, id) {
            var row = $$("datatable_{{ model_name }}").getItem(id);
            row['checkbox_action'] = true;
        })
        {% if not is_json_loading %}
        $$('select_all_checkbox').setValue(1);
        {% endif %}
    } else {
        $$("datatable_{{ model_name }}").eachRow(function (id) {
            row = this.getItem(id);
            if (row != undefined) {
                row['checkbox_action'] = undefined;
            }
        });
    }
    $$("datatable_{{ model_name }}").refresh();
    update_counter();
}

function prepare_actions_execute(action_name) {
    var ids = [];
    $$("datatable_{{ model_name }}").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id)
        }
    })
    if (ids.length > 0) {
        var all = $$('select_all_checkbox').getValue()==1;
        actions_execute(action_name, ids, all);
    } else {
        webix.alert("{{_("No row has been selected")|escapejs}}", "alert-warning");
    }
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
$$("{{ webix_container_id }}").addView({
    view: "toolbar",
    margin: 5,
    id: "{{ webix_container_id }}_toolbar",
    height: 65,
    cols: toolbar_actions.concat([
        {id: 'stats_list', view: 'label', label: '', width: 340},
        {id: 'select_all_checkbox', view: 'checkbox', value: 0, hidden:true},

        {% block toolbar_middle %}
        {$template: "Spacer"},
        {% endblock %}

        {% block add_button %}
        {% if has_add_permission or not remove_disabled_buttons and not has_add_permission %}
        {
            view: "tootipButton",
            type: "form",
            align: "right",
            label: '{{_("Add new")|escapejs}}',
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
//$$("datatable_{{ model_name }}").attachEvent("onCheck", function (row, column, state) {
 //   update_counter()
//});
