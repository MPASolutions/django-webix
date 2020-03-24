{% load django_webix_utils static i18n %}

{% block webix_content %}

{% block context_cleaner %}
webix.ui([], $$("{{ webix_container_id }}"));
{% endblock %}

{% block filter_options %}
        {% for field_name, choices_filter in choices_filters.items %}
            var {{ field_name }}_options = {{ choices_filter|safe }}
        {% endfor %}
{% endblock %}

        {% block toolbar_navigation %}
        {% if title %}
        $$("{{ webix_container_id }}").addView({
            id: 'main_toolbar_navigation',
            view: "toolbar",
            margin: 5,
            cols: [
                {
                    id: 'filter_{{ model_name }}',
                    view: "text",
                    value: "1",
                    hidden: true,
                },
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

function get_filters_qsets() {
    var qsets = [];

    $.each($$('datatable_{{ model_name }}').config.columns, function (index, el) {
        el = $$('datatable_{{ model_name }}').config.columns[index];
        ds_filter = $$('datatable_{{ model_name }}').getFilter(el.id);
        if ((ds_filter != null) && (ds_filter != undefined)) {
            if (ds_filter.getValue != undefined) {
                value = ds_filter.getValue();
            } else {
                value = ds_filter.value;
            }
            if ((value != '') && (value != undefined)) {
                if (el.serverFilterType == 'numbercompare') {
                    var val = value;
                    val = val.split(' ').join('');
                    val = val.split(';')
                    $.each(val, function (index, filter_txt) {
                        if (isNumberCheck(filter_txt)) {
                            qsets.push({'path': el.id, 'val': filter_txt});
                        } else if ((filter_txt.substring(0, 2) == '>=') && (isNumberCheck(filter_txt.substring(2)))) {
                            qsets.push({'path': el.id + '__gte', 'val': filter_txt.substring(2)});
                        } else if ((filter_txt.substring(0, 2) == '<=') && (isNumberCheck(filter_txt.substring(2)))) {
                            qsets.push({'path': el.id + '__lte', 'val': filter_txt.substring(2)});
                        } else if ((filter_txt.substring(0, 1) == '>') && (isNumberCheck(filter_txt.substring(1)))) {
                            qsets.push({'path': el.id + '__gt', 'val': filter_txt.substring(1)});
                        } else if ((filter_txt.substring(0, 1) == '<') && (isNumberCheck(filter_txt.substring(1)))) {
                            qsets.push({'path': el.id + '__lt', 'val': filter_txt.substring(1)});
                        }
                    })
                } else {
                    qsets.push({'path': el.id + '__' + el.serverFilterType, 'val': value});
                }
            }
        }
    });

    return {
        'operator': 'AND',
        'qsets': qsets
    }
}

{% block datatable %}
$$("{{ webix_container_id }}").addView({
    id: 'datatable_{{ model_name }}',
    view: "datatable",
    leftSplit: 1,
    //sort:"multi", // not works
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
            header: [
                {content: "headerMenu"},
                {text: "<input name='master_checkbox' style='width: 22px;height: 22px;' type='checkbox' onclick='master_checkbox_click()'>"}
            ],
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
        {
            id: "cmd_cp",
            header: [
                {
                    text: "",
                    colspan: 2
                },
                {
                    text: '<div class="webix_view webix_control webix_el_button webix_secondary"><div title="Applica i filtri impostati" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="$$(\'filter_{{ model_name }}\').setValue(\'1\');$$(\'datatable_{{ model_name }}\').filterByAll();"> Applica </button></div></div>',
                    colspan: 2
                }
            ],
            adjust: "data",
            headermenu: false,
            tooltip: false,
            template: {% if has_add_permission and is_enable_column_copy %}custom_button_cp{% else %}""{% endif %}
        },
        {
            id: "cmd_rm",
            header: "",
            adjust: "data",
            headermenu: false,
            tooltip: false,
            template: {% if has_delete_permission and is_enable_column_delete %}custom_button_rm{% else %}""{% endif %}
        }
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
            _params.filters = JSON.stringify( get_filters_qsets() );
            //$$('filter_{{ model_name }}').setValue('0');

            // elaborate sort
            sort = $$('datatable_{{ model_name }}').getState().sort;
            if (sort != undefined) {
                if (sort.dir == 'desc') {
                    _params.sort = ['-' + sort.id]
                } else {
                    _params.sort = ['' + sort.id]
                }
            }

            return webix.ajax().bind(view).post(this.source, $.param(_params))
                    .then(function (data) {
                        _data = data.json();
                        $$('datatable_{{ model_name }}').view_count = _data.data.length;
                        $$('datatable_{{ model_name }}').view_count_total = _data.total_count;
                        update_counter();
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
    clipboard: true,
    {% endif %}
    navigation: true,
    checkboxRefresh: true,
    on: {
        onCheck: function (row, column, state) {
            update_counter();
        },
        onBeforeLoad: function () {
            this.showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        },
        onBeforeFilter: function (id) {
            this.getFilter(id).disabled = true;
            console.log(id,'before filter','filter_{{ model_name }}', $$('filter_{{ model_name }}').getValue() , $$('filter_{{ model_name }}').getValue() == '0')

            if ($$('filter_{{ model_name }}').getValue() == '0') {
                console.log('before filter FALSE',$$('filter_{{ model_name }}').getValue())
                return false
            }
        },
        onAfterFilter: function () {
            console.log('after filter')
            var columns = this.config.columns;
            columns.forEach(function (obj) {
                if ($$("datatable_{{model_name}}").getFilter(obj.id)) {
                    $$("datatable_{{model_name}}").getFilter(obj.id).disabled = false;
                }
            });
            $$('filter_{{ model_name }}').setValue('0');
        },
        onItemDblClick: function (id, e, trg) {
            var el = $$('datatable_{{model_name}}').getSelectedItem();
            {% block datatable_onitemdoubleclick %}
            {% if is_enable_row_click and type_row_click == 'double' %}
            load_js('{{ url_update }}'.replace('0', el.id));
            {% endif %}
            {% endblock %}
        },
        onAfterLoad: function () {
            {% if not is_json_loading %}
            $$('datatable_{{ model_name }}').view_count = objects_list.length;
            $$('datatable_{{ model_name }}').view_count_total = objects_list.length;
            {% endif %}
            this.hideOverlay();
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

//% block orders %}
//grid.markSorting("title", "asc");
//% endblock %}

{% block footer %}
{% if footer %}
$$("datatable_{{model_name}}").define("footer", true);
$$("datatable_{{model_name}}").refresh();
{% for field_name, field_value in footer.items %}
$$('datatable_{{model_name}}').getColumnConfig('{{ field_name }}'.replace('_footer', '')).footer[0].text = "{{ field_value }}"
$$('datatable_{{model_name}}').refreshColumns();
{% endfor %}
{% endif %}
{% endblock %}

{%  if is_json_loading %}

$$("{{ webix_container_id }}").addView({
    template: "{common.first()} {common.prev()} {common.pages()} {common.next()} {common.last()}",
    id: "datatable_paging_{{ model_name }}", // the container to place the pager controls into
    view: "pager",
    group: 5, // buttons for next amd back
    // must to be the same of url request because managed from interface
    size: {{ paginate_count_default }},
    page: 0,
    on: {
        onBeforePageChange: function (new_page, old_page) {
            if ($('input[name="master_checkbox"]').prop("checked") == true) {
                $('input[name="master_checkbox"]').click();
                update_counter();
            }
        }
    }
})
{% else %}
$$('filter_{{ model_name }}').setValue('0');
{% endif %}

{% endblock %}

{% block toolbar_list %}
/*
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
}*/
function win_actions_execute(action, ids, all) {
    $$('datatable_{{model_name}}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "{{ url_list }}");
    form.setAttribute("target", "view");
    _fields = [
        ['action',action],
        ['filters', JSON.stringify( get_filters_qsets() )],
        ['csrfmiddlewaretoken',getCookie('csrftoken')]
    ];
    if (all==false){
        _fields.push(['ids',ids.join(',')])
    }
    $.each(_fields, function( index, value ) {
        var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", value[0]);
            hiddenField.setAttribute("value", value[1]);
            form.appendChild(hiddenField);
        });
    document.body.appendChild(form);
    window.open('', 'view');
    form.submit();
    $$('datatable_{{model_name}}').hideOverlay();
}

function delete_actions_execute(action, ids, all) {
    webix.confirm({
        title: '{{ _("Delete")|escapejs|upper }}',
        ok: '{{ _("Proceed")|escapejs }}',
        cancel: '{{ _("Undo")|escapejs }}',
        text: "{% trans "Are you sure you want to proceed with this action?" %} </br> <b>" + ids.length + " {% trans "elements" %}</b> {% trans "selected" %}",
        callback: function (result) {
            if (result) {
                _params = {
                    'action': action,
                    'filters': JSON.stringify(get_filters_qsets()),
                    'csrfmiddlewaretoken': getCookie('csrftoken')
                };
                if (all == false) {
                    _params['ids'] = ids.join(',');
                }
                $.ajax({
                    url: "{{ url_list }}",
                    //dataType: "json",
                    type: "POST",
                    data: _params,
                    error: function (data) {
                        webix.message({
                            text: "{% trans "Action is not executable" %}",
                            type: "error",
                            expire: 10000
                        });
                    },
                    success: function (data) {
                        webix.message({
                            text: data.message,
                            type: "info",
                            expire: 5000
                        });
                        load_js('{{ url_list }}');
                    },
                });
            }
        }
    })
}

{% block toolbar_list_actions %}
{% if is_enable_actions %}
var actions_list = [
    {% for action_key, action_verbose_name in actions.items %}
    {id: '{{ action_key }}', value: '{{action_verbose_name}}'}{% if not forloop.last %}, {% endif %}
    {% endfor %}
];
function actions_execute(action, ids, all) {
    if (action=='delete'){
        delete_actions_execute(action, ids, all);
    } else {
        var action_names = [{% for action_key, action in actions.items %}'{{ action_key }}'{% if not forloop.last %}, {% endif %}{% endfor %}];
        if (action_names.includes(action) == true) {
            win_actions_execute(action, ids, all);
        }
    }

}
{% else %}
var actions_list = undefined;
var actions_execute = undefined;
{% endif %}
{% endblock %}

{% include "django_webix/include/toolbar_list.js" %}
{% endblock %}

{% block extrajs_post %}{% endblock %}
{% endblock %}
