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

{% if geo_filter %}
var {{ view_prefix }}geo_filter = '{{ geo_filter|escapejs }}';
{% else %}
var {{ view_prefix }}geo_filter = undefined;
{% endif %}

{% if sql_filters %}
var {{ view_prefix }}sql_filters = '{{ sql_filters|escapejs }}';
{% else %}
var {{ view_prefix }}sql_filters = undefined;
{% endif %}

{% if qsets_locked_filters %}
var {{ view_prefix }}locked_filters = '{{ qsets_locked_filters|escapejs }}';
{% else %}
var {{ view_prefix }}locked_filters = undefined;
{% endif %}

var {{ view_prefix }}django_webix_filters = [{% for f in django_webix_filters %}{{ f.pk }}{% if not forloop.last %},{% endif %}{% endfor %}];

        {% block toolbar_navigation %}
        {% if title %}
        $$("{{ webix_container_id }}").addView({
            id: '{{ view_prefix }}main_toolbar_navigation',
            view: "toolbar",
            margin: 5,
            cols: [
                {
                    id: '{{ view_prefix }}filter',
                    view: "text",
                    value: "1",
                    hidden: true,
                },
                {},
                {
                    view: "template",
                    type: "header",
                    borderless: true,
                    template: '<div style="width:100%; text-align:center;"><strong>{{ title }}</strong></div>'
                },
                {},
                {
                    view: "button",
                    label: "{{_("Extra filters removal")|escapejs}}",
                    type: "icon",
                    width: 200,
                    hidden: ({{ view_prefix }}locked_filters==undefined) && ({{ view_prefix }}sql_filters==undefined),
                    icon: "far fa-trash-alt",
                    click: function (id, event) {
                        load_js('{{ url_list }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    }
                },
                {
                    view: "button",
                    label: "{{_("Geographic filter removal")|escapejs}}",
                    type: "icon",
                    width: 200,
                    hidden: ({{ view_prefix }}geo_filter==undefined),
                    icon: "far fa-trash-alt",
                    click: function (id, event) {
                        load_js('{{ url_list }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    }
                },
                {% if is_installed_django_webix_filter %}
                {
                    view: "button",
                    label: "{{_("Advanced filter")|escapejs}} <div class='webix_badge' style='background-color: #ff8839 !important;' id='{{ view_prefix }}django_webix_filter_counter'>0</div>",
                    type: "icon",
                    width: 180,
                    //hidden: django_webix_filters.length==0,
                    icon: "far fa-filter",
                    click: function (id, event) { // (lnk, hide, area, method, data)
                        load_js('{% url 'django_webix_filter.webixfilter.list_model' app_label=app_label model_name=module_name %}?_popup', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    }
                },
                {% endif %}
            ]
        });
{% endif %}
{% endblock %}

{% block objects_list %}
{% if not is_json_loading %}
var {{ view_prefix }}objects_list = [
    {% for obj in objects_datatable %}
    {status: 0,
    {% for key, value in obj.items %}
    {{ key }}: "{{ value|format_list_value|escapejs }}"{% if not forloop.last %}, {% endif %}
    {% endfor %}
    {% block extra_columns %}{% endblock %}
    }{% if not forloop.last %}, {% endif %}
    {% endfor %}
]
{% endif %}
{% endblock %}

function {{ view_prefix }}get_filters_qsets() {
    var qsets = [];

    $.each($$('{{ view_prefix }}datatable').config.columns, function (index, el) {
        el = $$('{{ view_prefix }}datatable').config.columns[index];
        ds_filter = $$('{{ view_prefix }}datatable').getFilter(el.id);
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

function {{ view_prefix }}apply_filters(){
  $('#{{ view_prefix }}django_webix_filter_counter').text({{ view_prefix }}django_webix_filters.length);
  $$('{{ view_prefix }}filter').setValue('1');
  $$('{{ view_prefix }}datatable').filterByAll();
  }

$$("{{ webix_container_id }}").addView({
    id: '{{ view_prefix }}datatable',
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
                {text: "<input name='{{ view_prefix }}master_checkbox' style='width: 22px;height: 22px;' type='checkbox' onclick='{{ view_prefix }}master_checkbox_click()'>"}
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
                    text: '<div class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Apply filters") }}" class="webix_el_box"><button type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="{{ view_prefix }}apply_filters(\'{{ model_name }}\');"> {{_("Filter") }} </button></div></div>',
                    colspan: 2
                }
            ],
            headermenu: false,
            width:40,
            tooltip: false,
            template: {% if has_add_permission and is_enable_column_copy %}custom_button_cp{% else %}'<div><i style="cursor:pointer" class="webix_icon far"></i></div>'{% endif %}
        },
        {
            id: "cmd_rm",
            header: "",
            headermenu: false,
            width:40,
            tooltip: false,
            template: {% if has_delete_permission and is_enable_column_delete %}custom_button_rm{% else %}'<div><i style="cursor:pointer" class="webix_icon far"></i></div>'{% endif %}
        }
        {% endblock %}
    ],
    {%  if is_json_loading %}
    datafetch: {{ paginate_count_default }},
    pager: "datatable_paging_{{ model_name }}",
    url: {
        $proxy: true,
        source: "{{ url_list }}{% if '?' in url_list %}&{% else %}?{% endif %}json",
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
            _params.filters = JSON.stringify( {{ view_prefix }}get_filters_qsets() );

            if ({{ view_prefix }}geo_filter!=undefined) {
                _params.geo_filter = {{ view_prefix }}geo_filter;
            }

            if ({{ view_prefix }}sql_filters!=undefined) {
                _params.sql_filters = {{ view_prefix }}sql_filters;
            }

            if ({{ view_prefix }}locked_filters!=undefined) {
                _params.locked_filters = {{ view_prefix }}locked_filters;
            }

            if ({{ view_prefix }}django_webix_filters!=undefined) {
                _params.django_webix_filters = {{ view_prefix }}django_webix_filters;
            }


            // elaborate sort
            sort = $$('{{ view_prefix }}datatable').getState().sort;
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
                        $$('{{ view_prefix }}datatable').view_count = _data.data.length;
                        $$('{{ view_prefix }}datatable').view_count_total = _data.total_count;
                        // counter
                        {{ view_prefix }}update_counter();
                        {% if is_enable_footer %}
                        // footer only for first page
                        for (var field_name in _data.footer) {
                            $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).footer[0].text = _data.footer[field_name];
                        }
                        //$$('{{ view_prefix }}datatable').refreshColumns(); // will be refreshed alone
                        {% endif %}
                        return data;
                    })
                    .fail(function (err) {
                    })
                    .finally(function () {
                    });
        }
    },
    {% else %}
    data: {{ view_prefix }}objects_list,
    {% endif %}
    navigation: true,
    checkboxRefresh: true,
    on: {
        onCheck: function (row, column, state) {
            {{ view_prefix }}update_counter();
        },
        onBeforeFilter: function (id) {
            if ($$('{{ view_prefix }}filter').getValue() == '0') {
                return false
            } else {
                $$("{{ view_prefix }}datatable").getFilter(id).disabled = true;
            }
        },

        onAfterFilter: function () {
            var columns = this.config.columns;
            columns.forEach(function (obj) {
                if ($$("{{ view_prefix }}datatable").getFilter(obj.id)) {
                    $$("{{ view_prefix }}datatable").getFilter(obj.id).disabled = false;
                }
            });
            $$('{{ view_prefix }}filter').setValue('0');
        },
        onBeforeLoad: function () {
            this.showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        },
        onAfterLoad: function () {
            {% if not is_json_loading %}
            $$('{{ view_prefix }}datatable').view_count = {{ view_prefix }}objects_list.length;
            $$('{{ view_prefix }}datatable').view_count_total = {{ view_prefix }}objects_list.length;
            {% endif %}
            this.hideOverlay();
        },
        onItemDblClick: function (id, e, trg) {
            var el = $$('{{ view_prefix }}datatable').getSelectedItem();
            {% block datatable_onitemdoubleclick %}
            {% if is_enable_row_click and type_row_click == 'double' %}
            load_js('{{ url_update }}'.replace('0', el.id), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
            {% endif %}
            {% endblock %}
        },
        onItemClick: function (id, e, trg) {
            var el = $$('{{ view_prefix }}datatable').getSelectedItem();
            {% block datatable_onitemclick %}
            {% for field in fields %}
            {% if field.click_action %}
            if ((id.column == '{{ field.field_name }}') || (id.column == '{{ field.column_name }}')) {
                {{ field.click_action|safe }};
            } else
                    {% endif %}
                    {% endfor %}
            if (id.column == 'cmd_cp') {
                {% block cmd_cp_click %}
                    {% if is_enable_column_copy %}
                        load_js('{{ url_create }}?pk_copy=' + el.id, undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    {% endif %}
                {% endblock %}
            } else if (id.column == 'cmd_rm') {
                {% block cmd_rm_click %}
                    {% if is_enable_column_delete %}
                        load_js('{{ url_delete }}'.replace('0', el.id), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    {% endif %}
                {% endblock %}
            } else {
                {% if is_enable_row_click %}
                    {% if type_row_click == 'single' %}
                    load_js('{{ url_update }}'.replace('0', el.id), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    {% else %}
                    webix.message({type: "success", text: "{{_("Double click to edit the element")|escapejs}}"});
                    {% endif %}
                {% endif %}
            }
            {% endblock %}
        }
    }
});

{% block footer %}
    {% if is_enable_footer %}
        $$("{{ view_prefix }}datatable").define("footer", true);
        $$("{{ view_prefix }}datatable").refresh();
        {%  if not is_json_loading %}
            {% for field_name, field_value in footer.items %}
                $$('{{ view_prefix }}datatable').getColumnConfig('{{ field_name }}'.replace('_footer', '')).footer[0].text = "{{ field_value }}"
            {% endfor %}
            $$('{{ view_prefix }}datatable').refreshColumns();
        {% endif %}
    {% endif %}
{% endblock %}

// disable filter on first request
$$('{{ view_prefix }}filter').setValue('0');

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
            if ($('input[name="{{ view_prefix }}master_checkbox"]').prop("checked") == true) {
                $('input[name="{{ view_prefix }}master_checkbox"]').click();
                {{ view_prefix }}update_counter();
            }
        }
    }
})
{% endif %}

{% endblock %}

{% block toolbar_list %}

function _{{ view_prefix }}action_execute(action, ids, all, response_type, short_description, modal_title, modal_ok, modal_cancel) {
    /*
    action (required) = action_key to be executed
    ids (required) = list of selected elements ids
    all (required) = boolean if all elements are selected
    response_type (required) = ['script', 'json', 'blank']
    short_description (not required)
    modal_title (required) = text to show in modal choices execution
    modal_ok (not required)
    modal_cancel (not required)
    */
    webix.confirm({
        title: short_description,
        ok: modal_ok,
        cancel: modal_cancel,
        text:  modal_title + "</br><b>" + ids.length + " {{_("elements")|escapejs}}</b> {{_("selected")|escapejs}}",
        callback: function (confirm) {
            if (confirm==true) {
                $$('{{ view_prefix }}datatable').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                if ((response_type=='json') || (response_type=='script')){
                    _params = {
                        'action': action,
                        'filters': JSON.stringify({{ view_prefix }}get_filters_qsets()),
                        'csrfmiddlewaretoken': getCookie('csrftoken')
                    };
                    if (all == false) {
                        _params['ids'] = ids.join(',');
                    }
                    $.ajax({
                        url: "{{ url_list }}",
                        type: "POST",
                        dataType: response_type,
                        data: _params,
                        error: function (data) {
                            webix.message({
                                text: "{{_("Action is not executable")|escapejs}}",
                                type: "error",
                                expire: 10000
                            });
                        },
                        success: function (data) { // TODO gestire response
                            if (data.status==true) {
                                webix.message({
                                    text: data.message,
                                    type: "info",
                                    expire: 5000
                                });
                                if (data.redirect_url!=null){
                                    load_js(data.redirect_url, undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                                    }
                            } else {
                                webix.message({
                                    text: "{{_("Something gone wrong")|escapejs}}",
                                    type: "error",
                                    expire: 10000
                                });
                            }
                        },
                    });
                } else if (response_type=='blank'){
                    var form = document.createElement("form");
                    form.setAttribute("method", "post");
                    form.setAttribute("action", "{{ url_list }}");
                    form.setAttribute("target", "view");
                    _fields = [
                        ['action',action],
                        ['filters', JSON.stringify( {{ view_prefix }}get_filters_qsets() )],
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
                } else {

                }
                $$('{{ view_prefix }}datatable').hideOverlay();
            }
        }
    })
}

{% block toolbar_list_actions %}
{% if is_enable_actions %}

var {{ view_prefix }}actions_list = [
    {% for action_key,action in actions.items %}
    {id: '{{ action_key }}', value: '{{action.short_description}}'}{% if not forloop.last %}, {% endif %}
    {% endfor %}
];

function {{ view_prefix }}actions_execute(action, ids, all) {
    {% for action_key, action in actions.items %} if (action=='{{ action_key }}') {
        _{{ view_prefix }}action_execute(
                '{{ action_key }}',
                ids,
                all,
                '{{ action.response_type }}',
                '{{ action.short_description }}',
                '{{ action.modal_title }}',
                '{{ action.modal_ok }}',
                '{{ action.modal_cancel }}'
        )
    } {% if not forloop.last %} else {% endif %} {% endfor %}

}
{% else %}
var {{ view_prefix }}actions_list = undefined;
var {{ view_prefix }}actions_execute = undefined;
{% endif %}
{% endblock %}

{% include "django_webix/include/toolbar_list.js" %}
{% endblock %}

{% block extrajs_post %}{% endblock %}
{% endblock %}
