{% load django_webix_utils static i18n %}

{% block webix_content %}

{% block context_cleaner %}
webix.ui([], $$("{{ webix_container_id }}"));
{% endblock %}

{% block toolbar_navigation %}
{% if title %}
$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {},
        {
            view: "template",
            type: "header",
            template: '<div style="width:100%; text-align:center;"><strong>{{ title }}</strong></div>'
        },
        {},
        {% if is_filters_active or is_sql_filters_active %}
        {
            view: "button",
            label: "{% trans 'Filters removal' %}",
            type: "icon",
            width: 170,
            icon: "far fa-trash-alt",
            click: function (id, event) {
                load_js('{{ url_list }}');
            }
        },
        {% endif %}
        {% if is_geo_filter_active %}
        {
            view: "button",
            label: "{% trans 'Geographic filter removal' %}",
            type: "icon",
            width: 170,
            icon: "far fa-trash-alt",
            click: function (id, event) {
                load_js('{{ url_list }}');
            }
        },
        {% endif %}
    ]
});
{% endif %}
{% endblock %}

{% block objects_list %}
{% if not is_json_loading %}
var objects_list = [
    {% for obj in objects_datatable %}
    {
        status: 0,
{% for key, value in obj.items %}
{{ key }}: "{{ value|format_list_value|escapejs }}"{% if not forloop.last %}, {% endif %}
{% endfor %}
{% block extra_columns %}{% endblock %}
}{% if not forloop.last %}, {% endif %}
{% endfor %}
]
{% endif %}
{% endblock %}

{% block datatable %}
$$("{{ webix_container_id }}").addView({
    id: 'datatable_{{ model_name }}',
    view: "datatable",
    leftSplit: 1,
    select: "row",
    resizeColumn: true,
    {% block datatable_headermenu %}
    headermenu: {
        width: 250
    },
    {% endblock %}
    columns: [
        {
            id: "checkbox_action",
            header: [{content: "headerMenu"}, {content: "masterCheckbox", css: "center"}],
            template: "{common.checkbox()}",
            tooltip: false,
            headermenu: false,
            width: 40,
            minWidth: 40,
            maxWidth: 40,
            css: {'text-align': 'right'}
        },
        {% block datatable_columns %}
        {% for field in fields %}
        {{ field.datalist_column|safe }},
        {% endfor %}
        {% endblock %}
        {% block datatable_columns_commands %}
        {% if has_add_permission %}
        {% if is_enable_column_copy %}
        {
            id: "cmd_cp",
            header: "",
            adjust: "data",
            headermenu: false,
            tooltip: false,
            template: custom_button_cp
        },
        {% endif %}
        {% endif %}
        {% if has_delete_permission %}
        {% if is_enable_column_delete %}
        {
            id: "cmd_rm",
            header: "",
            adjust: "data",
            headermenu: false,
            tooltip: false,
            template: custom_button_rm
        }
        {% endif %}
        {% endif %}
        {% endblock %}
    ],
    {%  if is_json_loading %}
    datafetch: {{ paginate_count_default }},
    pager: "datatable_paging_{{ model_name }}",
    url: {
        $proxy: true,
        source: "{{ url_list }}?json",
        load: function (view, params) {
            // elaborate paging
            var _count = {{ paginate_count_default }};
            var _start = 0;
            if ((params) && (params.count)) {
                _count = params.count;
            }
            if ((params) && (params.start)) {
                _start = params.start;
            }
            var _params = {
                'start': _start,
                'count': _count,
            }
            // elaborate filters
            var qsets = [];
            $.each($$('datatable_{{ model_name }}').config.columns, function (index, el) {
                el = $$('datatable_{{ model_name }}').config.columns[index];
                key = el.id + '';
                ds_filter = $$('datatable_{{ model_name }}').getFilter(el.id)
                if ((ds_filter != null) && (ds_filter != undefined)) {
                    if (ds_filter.value != '') {
                        // TODO: aggiungere __icontains per text ECCETERA
                        qsets.push({'path': key, 'val': ds_filter.value});
                    }
                } else {
                    //qsets.push({'path': key,'val':''});
                }
            })

            _params.filters = JSON.stringify({
                'operator': 'AND',
                'qsets': qsets
            })
            return webix.ajax().bind(view).post(this.source, $.param(_params))
                .then(function (data) {
                    //data.total_count
                    update_counter(); // for future must be function of datalist not generical
                    return data;
                })
                .fail(function (err) {
                })
                .finally(function () {
                });
        }
    },
    {% else %}
    data: objects_list,
    {% endif %}
    navigation: true,
    checkboxRefresh: true,
    //ready: function () {
    //    $$("datatable_{{ model_name }}").load('{{ url_list }}?json');
    //    $$("datatable_{{ model_name }}").filterByAll();
    //},
    on: {
        onItemDblClick: function (id, e, trg) {
            var el = $$('datatable_{{model_name}}').getSelectedItem();
            {% block datatable_onitemdoubleclick %}
            {% if is_enable_row_click and type_row_click == 'double' %}
            load_js('{{ url_update }}'.replace('0', el.id));
            {% endif %}
            {% endblock %}
        },
        onItemClick: function (id, e, trg) {
            var el = $$('datatable_{{model_name}}').getSelectedItem();
            {% block datatable_onitemclick %}
            {% for field in fields %}
            {% if field.click_action %}
            if ((id.column == '{{ field.field_name }}') || (id.column == '{{ field.column_name }}')) {
                {{ field.click_action|safe }};
            } else
                {% endif %}
                {% endfor %}
            if (id.column == 'cmd_cp') {
                load_js('{{ url_create }}?pk_copy=' + el.id);
            } else if (id.column == 'cmd_rm') {
                load_js('{{ url_delete }}'.replace('0', el.id));
            } else {
                {% if is_enable_row_click and type_row_click == 'single' %}
                load_js('{{ url_update }}'.replace('0', el.id));
                {% else %}
                webix.message({type: "success", text: "{% trans "Double click to edit the element" %}"});
                {% endif %}
            }
            {% endblock %}
        }
    }
});

{%  if is_json_loading %}

$$("{{ webix_container_id }}").addView({
    template: "{common.first()} {common.prev()} {common.pages()} {common.next()} {common.last()}",
    id: "datatable_paging_{{ model_name }}", // the container to place the pager controls into
    view: "pager",
    group: 5, // buttons for next amd back
    // must to be the same of url request because managed from interface
    size: {{ paginate_count_default }},
    page: 0,
})
{% endif %}

{% endblock %}

{% block toolbar_list %}
function webix_to_excel() {
    webix.toExcel(
        $$("datatable_{{model_name}}"),
        {
            filter: function (obj) {
                return obj.checkbox_action;
            },
            filename: "{% trans "Data" %}",
            name: "{% trans "Data" %}",
            filterHTML: true,
            ignore: {"checkbox_action": true, "cmd_rm": true, "cmd_cp": true}
        }
    );
}

{% block toolbar_list_actions %}
{% if is_enable_actions %}
var actions_list = [
    {id: "excel_standard", value: "EXCEL: {% trans "Data export" %}"}
];
function actions_execute(action, ids) {
    if (action == "excel_standard") {
        webix_to_excel()
    }
}
{% endif %}
{% endblock %}

{% include "django_webix/include/toolbar_list.js" %}
{% endblock %}

{% block extrajs_post %}{% endblock %}
{% endblock %}
