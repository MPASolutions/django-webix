{% load django_webix_utils static i18n filtersmerger_utils %}
{% get_request_filter_params %}

{% block webix_content %}

{% block context_cleaner %}
webix.ui([], $$("{{ webix_container_id }}"));
{% endblock %}

{% if model %}
initWebixFilterPrefix('{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}');
{% endif %}

{% block filter_options %}
    {% for field_name, choices_filter in choices_filters.items %}
        var {{ field_name }}_options = {{ choices_filter|safe }}
    {% endfor %}
{% endblock %}

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
            value: "0", // disable by default
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
            id: '{{ view_prefix }}_filter_locked_sql',
            view: "button",
            label: "{{_("Extra filters removal")|escapejs}}",
            type: "icon",
            width: 200,
            hidden: true,
            icon: "far fa-trash-alt",
            click: function (id, event) {
                {% if model %}
                {% for key, param in extra_filter_params.items %}{% if param %}
                setWebixFilter('{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}', '{{ param }}', null);
                {% endif %}{% endfor %}
                {% endif %}
                load_js('{{ url_list }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
            }
        },
        {
            id: '{{ view_prefix }}_filter_geo',
            view: "button",
            label: "{{_("Geographic filter removal")|escapejs}}",
            type: "icon",
            width: 200,
            hidden: true,
            icon: "far fa-trash-alt",
            click: function (id, event) {
                {% if model %}
                {% for key, param in spatial_filter_params.items %}{% if param %}
                setWebixFilter('{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}', '{{ param }}', null);
                {% endif %}{% endfor %}
                {% endif %}
                load_js('{{ url_list }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
            }
        },
        {% if is_installed_django_webix_filter %}
        {
            id: '{{ view_prefix }}_filter_advanced',
            view: "button",
            label: "{{_("Advanced filter")|escapejs}} <div class='webix_badge' style='background-color: #ff8839 !important;' id='{{ view_prefix }}django_webix_filter_counter'>0</div>",
            type: "icon",
            width: 180,
            icon: "far fa-filter",
            click: function (id, event) { // (lnk, hide, area, method, data)
                load_js('{% url 'django_webix_filter.webixfilter.list_model' app_label=app_label model_name=module_name %}?_popup', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
            }
        },
        {% endif %}

    ]
});

{% if model %}
if (
    false
    {% for key, param in extra_filter_params.items %}{% if param %}
    || (webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']['{{ param }}'] != null)
    {% endif %}{% endfor %}
) {
    $$('{{ view_prefix }}_filter_locked_sql').show();
}
if (
    false
    {% for key, param in spatial_filter_params.items %}{% if param %}
    || (webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']['{{ param }}'] != null)
    {% endif %}{% endfor %}
) {
    $$('{{ view_prefix }}_filter_geo').show();
}
{% endif %}

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
                    if ((el.serverFilterType=='') || (el.serverFilterType==undefined)){
                        qsets.push({'path': el.id, 'val': value});
                    } else{
                        qsets.push({'path': el.id + '__' + el.serverFilterType, 'val': value});
                    }
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

function {{ view_prefix }}is_active_otf_filter(){
    var key = '{{ model_name }}';
    if(typeof otf_filter !== "undefined") {
        if (otf_filter[key] != undefined) {
            if (otf_filter[key]['list'] != undefined) {
                if (otf_filter[key]['list']['active']) {
                    return true;
                }
            }
        }
    }
    return false;
}

function {{ view_prefix }}is_present_otf_filter(){
    var key = '{{ model_name }}';
    if(typeof otf_filter !== "undefined") {
        if (otf_filter[key] != undefined) {
            if (otf_filter[key]['list'] != undefined) {
                if (otf_filter[key]['list']['json'] != undefined) {
                    return true;
                }
            }
        }
    }
    return false;
}

function {{ view_prefix }}get_otf_filter(){
    var key = '{{ model_name }}';
    if(typeof otf_filter !== "undefined") {
        if (otf_filter[key] != undefined) {
            if (otf_filter[key]['list'] != undefined) {
                if (otf_filter[key]['list']['json'] != undefined) {
                    return otf_filter[key]['list']['json'];
                }
            }
        }
    }
    return undefined;
}

function {{ view_prefix }}deactivate_otf_filter(){
    var key = '{{ model_name }}';
    if(typeof otf_filter !== "undefined") {
        if (otf_filter[key] != undefined) {
            if (otf_filter[key]['list'] != undefined) {
                otf_filter[key]['list']['active'] = false;
                return true;
            }
        }
    }
    return false;
}

function {{ view_prefix }}apply_filters() {
    var extra = ''
    if({{ view_prefix }}is_active_otf_filter()){
        extra = '+';
    }
    var advanced_filter_count = '0';
    {% with param='DjangoAdvancedWebixFilter'|request_filter_param %}
    {% if param %}
    var advanced_filter = webixAppliedFilters['{{ model_name }}']['{{ param }}'];
    if (advanced_filter){
        advanced_filter_count = advanced_filter.split(',').length
    }
    {% endif %}
    {% endwith %}
    if(extra != '' && advanced_filter_count == '0'){
        advanced_filter_count = '';
    }
    $('#{{ view_prefix }}django_webix_filter_counter').text(advanced_filter_count + extra);
    $$('{{ view_prefix }}filter').setValue('1');
    $$('{{ view_prefix }}datatable').filterByAll();
}

{% if is_enable_column_webgis %}
{% for layer in layers %}
function custom_button_geo_{{layer.codename}}(obj, common, value) {
    if (obj.{{ layer.geofieldname }}_available==true)
        return '<div title="{{_("Go to map")|escapejs}} ({{layer.layername}})"><i style="cursor:pointer" class="webix_icon far fa-map-marker-alt"></i></div>';
    else
        return ''
}
{% endfor %}
{% endif %}

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
        {% if is_enable_column_webgis %}
            {% for layer in layers %}
                {
                    id: "cmd_gotomap_{{layer.codename}}",
                    header: "",
                    headermenu: false,
                    width:40,
                    tooltip: false,
                    template: custom_button_geo_{{layer.codename}}
                },
            {% endfor %}
        {% endif %}
        {
            id: "cmd_cp",
            {% if is_json_loading %}
            header: [
                {
                    text: "",
                    colspan: 2
                },
                {
                    text: '<div class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Apply filters") }}" class="webix_el_box"><button id="button_filter_datatable" type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="{{ view_prefix }}apply_filters(\'{{ model_name }}\');"> {{_("Filter") }} </button></div></div>',
                    colspan: 2
                }
            ],
            {% else %}
            header: "",
            {% endif %}
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
            {% if model %}
            var _params = webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}'];
            {% else %}
            var _params = {};
            {% endif %}
            _params.start = _start;
            _params.count = _count;
            // elaborate filters
            _params.filters = JSON.stringify( {{ view_prefix }}get_filters_qsets() );

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
    {% if is_json_loading %}
        onBeforeFilter: function (id) {
            if ($$('{{ view_prefix }}filter').getValue() == '0') {
                return false
            } else {
                if ($$("{{ view_prefix }}datatable").getFilter(id)) {
                    $$("{{ view_prefix }}datatable").getFilter(id).disabled = true;
                }
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
    {% endif %}
        onBeforeLoad: function () {
            this.showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        },
        onAfterLoad: function () {
            {% if not is_json_loading %}
            $$('{{ view_prefix }}datatable').view_count = {{ view_prefix }}objects_list.length;
            $$('{{ view_prefix }}datatable').view_count_total = {{ view_prefix }}objects_list.length;
            {% else %}
            $$('{{ view_prefix }}filter').setValue('0');
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
            {% if is_enable_column_webgis %}
            {% for layer in layers %}
            if ((id.column == 'cmd_gotomap_{{layer.codename}}')) {
                $$("map").goToWebgisPk('{{layer.qxsname}}', '{{ pk_field_name }}', el.id);
            } else
            {% endfor %}
            {% endif %}
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
},1);

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
// $$('{{ view_prefix }}filter').setValue('0');


{% endblock %}

{% block toolbar_list %}

{% include "django_webix/include/actions_utils.js" %}

{% block toolbar_list_actions %}
{% include "django_webix/include/actions_list.js" %}
{% endblock %}

{% include "django_webix/include/toolbar_list.js" %}
{% endblock %}

{{ view_prefix }}apply_filters();
{% block extrajs_post %}{% endblock %}
{% endblock %}
