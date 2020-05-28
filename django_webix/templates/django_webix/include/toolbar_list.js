{% load i18n %}

{# counter #}
function {{ view_prefix }}update_counter() {
    view_count = $$('{{ view_prefix }}datatable').view_count;
    view_count_total = $$('{{ view_prefix }}datatable').view_count_total;
    ids = [];
    $$("{{ view_prefix }}datatable").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id)
        }
    });
    if (ids.length!=view_count){
        $('input[name="{{ view_prefix }}master_checkbox"]').prop("checked",false) ;
        $$('{{ view_prefix }}select_all_checkbox').setValue(0);
    } else {
        $('input[name="{{ view_prefix }}master_checkbox"]').prop("checked",true) ;
        {% if not is_json_loading %}
        $$('{{ view_prefix }}select_all_checkbox').setValue(1);
        {% endif %}
    }
    if (ids.length > 0) {
        txt = ids.length + ' {{_("of")|escapejs}} ' + view_count_total + ' {{_("elements")|escapejs}}';
        {% if is_json_loading %}
        if (ids.length ==view_count) {
            if ($$('{{ view_prefix }}select_all_checkbox').getValue() == 0) {
                txt += '<div style="width:110px;float:right;height:100%;" class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Select all")|escapejs}}" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="$$(\'{{ view_prefix }}select_all_checkbox\').setValue(1);{{ view_prefix }}update_counter()"> {{_("Select all")|escapejs}} </button></div></div>';
            } else {
                txt = '{{_("All")|escapejs}} ' + view_count_total + ' {{_("elements selected")|escapejs}}';
                txt += '<div style="width:110px;float:right;height:100%;" class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Cancel selection")|escapejs}}" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="$$(\'{{ view_prefix }}select_all_checkbox\').setValue(0);$(\'input[name={{ view_prefix }}master_checkbox]\').prop(\'checked\',false);master_checkbox_click();{{ view_prefix }}update_counter()"> {{_("Cancel selection")|escapejs}} </button></div></div>';
            }
        }
        {% else %}
        if ($('input[name="{{ view_prefix }}master_checkbox"]').prop("checked") == true) {
            txt = '{{_("All")|escapejs}} ' + view_count_total + ' {{_("elements selected")|escapejs}}';
        }

        {% endif %}
    } else if (view_count_total!=undefined) {
        txt = view_count_total + ' {{_("elements")|escapejs}}';
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
            ids.push(id)
        }
        counter += 1;
    });
    {% else %}
    $$("{{ view_prefix }}datatable").eachRow(function (id) {
        ids.push(id)
        })
    {% endif %}
    return ids;
}


function {{ view_prefix }}master_checkbox_click() {
    $$('{{ view_prefix }}select_all_checkbox').setValue(0);
    if ($('input[name="{{ view_prefix }}master_checkbox"]').prop("checked") == true) {
        var ids = {{ view_prefix }}get_items_page_datatable()
        $.each(ids, function (index, id) {
            var row = $$("{{ view_prefix }}datatable").getItem(id);
            row['checkbox_action'] = true;
        })
        {% if not is_json_loading %}
        $$('{{ view_prefix }}select_all_checkbox').setValue(1);
        {% endif %}
    } else {
        $$("{{ view_prefix }}datatable").eachRow(function (id) {
            row = this.getItem(id);
            if (row != undefined) {
                row['checkbox_action'] = undefined;
            }
        });
    }
    $$("{{ view_prefix }}datatable").refresh();
    {{ view_prefix }}update_counter();
}

function {{ view_prefix }}prepare_actions_execute(action_name) {
    var ids = [];
    $$("{{ view_prefix }}datatable").eachRow(function (id) {
        if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
            ids.push(id)
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
    cols: {{ view_prefix }}toolbar_actions.concat([
        {id: '{{ view_prefix }}stats_list', view: 'label', label: '', width: 340},
        {id: '{{ view_prefix }}select_all_checkbox', view: 'checkbox', value: 0, hidden:true},

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
                load_js('{{ url_create }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
            }
        }
        {% endif %}
        {% endblock %}
    ])
});

{{ view_prefix }}update_counter();
