{% load django_webix_utils static i18n filtersmerger_utils %}
{% get_request_filter_params %}  // spatial_filter_params and extra_filter_params removal

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
    //autoheight:true, // to remove!!!
    cols: [
        {
            id: '{{ view_prefix }}filter',
            view: "text",
            value: "0", // disable by default
            hidden: true,
        },

        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><span style="text-align:center;"><strong>{{ title }}</strong></span></div>'
        },
        {% if is_json_loading %}
        {
            id: '{{ view_prefix }}_filter_extra',
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
                load_js('{{ url_list|safe }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
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
                load_js('{{ url_list|safe }}', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
            }
        },
        {% if is_installed_django_webix_filter and is_enabled_django_webix_filter %}
        {
            id: '{{ view_prefix }}_filter_advanced',
            view: "button",
            label: "{{_("Advanced filter")|escapejs}} <div class='webix_badge' style='background-color: #ff8839 !important;' id='{{ view_prefix }}django_webix_filter_counter'>0</div>",
            type: "icon",
            width: 180,
            icon: "far fa-filter",
            click: function (id, event) { // (lnk, hide, area, method, data)
                load_js('{% url 'dwfilter.webixfilter.list_model' app_label=app_label model_name=module_name %}?_popup', undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
            }
        },
        {% endif %}
        {% endif %}
    ]
});

var {{ view_prefix }}datatable_disable_savestate = true;

{% if is_json_loading %}

{% if model %}
if (
    false
    {% for key, param in extra_filter_params.items %}{% if param %}
    || (webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']['{{ param }}'] != null)
    {% endif %}{% endfor %}
) {
    $$('{{ view_prefix }}_filter_extra').show();
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

{% endif %}
{% endblock %}

{% if failure_change_blocking_objects %}
    {% include "django_webix/include/list_failure_blocking_objects.js"  with failure_blocking_objects=failure_change_blocking_objects %}
{% else %}
    {% if failure_change_related_objects %}
        {% block failure_related_objects %}
            {% include "django_webix/include/list_failure_related_objects.js" with failure_related_objects=failure_change_related_objects %}
        {% endblock %}
    {% else %}

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

        {% if is_editable %}
        var {{ view_prefix }}edit_mode_id = undefined;
        {% endif %}

        {% if is_json_loading %}
        {% include "django_webix/include/list_filters.js" %}
        {% endif %}

        {% block datatable %}

        {% if is_enable_column_webgis %}
        {% for layer in layers %}
        function custom_button_geo_{{layer.codename}}(obj, common, value) {
            {# we are making a controls as a string because the source may be string #}
            if (String(obj.{{ layer.geofieldname }}_available).toLowerCase() == "true")
                return '<div title="{{_("Go to map")|escapejs}} ({{layer.layername}})"><i style="cursor:pointer" class="webix_icon far fa-map-marker-alt"></i></div>';
            else
                return '<div title="{{_("Geometry does not exist")|escapejs}}"><i style="cursor:not-allowed" class="webix_icon far fa-map-marker-alt-slash"></i></div>'
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

        {%  if is_json_loading %}
        {% include "django_webix/include/list_state.js" %}
        var {{ view_prefix }}_first_load = true;
        {% endif %}


        $$("{{ webix_container_id }}").addView({
            id: '{{ view_prefix }}datatable',
            view: "datatable",
            {% if adjust_row_height %}
            fixedRowHeight: false,
            {% endif %}
            //sort:"multi", // not works
            select: "row",
            resizeColumn: true,
            {% block datatable_headermenu %}
            headermenu: {width: 250},
            {% endblock %}
            {% if is_editable %}
            editable:true,
            editaction: "custom",
            {% endif %}
            {% block right_split %}
            rightSplit:2,
            {% endblock %}
            {% block left_split %}
            leftSplit:1,
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
                    css: 'locked_column'
                },
                {% if is_editable %}
                {
                    id: "cmd_edit",
                    header: "",
                    headermenu: false,
                    width: 40,
                    tooltip: false,
                    template: '<div><i style="cursor:pointer" class="webix_icon fas fa-edit"></i></div>',
                    css: 'locked_column'
                },
                {% endif %}
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
                            // header: '<span title="{{_("Go to map")|escapejs}} ({{layer.layername}})" class="webix_icon fas fa-map-marked-alt"></span>',
                            header: '',
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
                        { text: '<div class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Remove filters") }}" class="webix_el_box"><button id="button_filter_datatable" type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="{{ view_prefix }}remove_filters(\'{{ model_name }}\');"><span class="webix_icon fas fa-undo"></span></button></div></div>', colspan: 2},
                        { text: '<div class="webix_view webix_control webix_el_button webix_secondary"><div title="{{_("Apply filters") }}" class="webix_el_box"><button id="button_filter_datatable" type="button" class="webix_button webix_img_btn" style="line-height:24px;" onclick="{{ view_prefix }}apply_filters(\'{{ model_name }}\');">{{_("Filter") }}</button></div></div>', colspan: 2},
                        {% if header_rows > 2 %}{ text:"", rowspan: {{header_rows|add:-2}} , colspan: 2}{% endif %}
                    ],
                    {% else %}
                    header: "",
                    {% endif %}
                    headermenu: false,
                    width: 40,
                    tooltip: false,
                    template: {% if has_add_permission and is_enable_column_copy %}custom_button_cp{% else %}'<div><i style="cursor:pointer" class="webix_icon far"></i></div>'{% endif %},
                    css: 'locked_column'
                },
                {
                    id: "cmd_rm",
                    header: "",
                    headermenu: false,
                    width: 40,
                    tooltip: false,
                    template: {% if has_delete_permission and is_enable_column_delete %}custom_button_rm{% else %}'<div><i style="cursor:pointer" class="webix_icon far"></i></div>'{% endif %},
                    css: 'locked_column'
                }
                {% endblock %}
            ],
            {%  if is_json_loading %}
            datafetch: {{ paginate_count_default }},
            pager: "datatable_paging_{{ model_name }}",
            url: {
                $proxy: true,
                source: "{{ url_list|safe }}{% if '?' in url_list %}&{% else %}?{% endif %}json",
                load: function (view, params) {
                        {% if model %}
                        var _params = webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}'];
                        {% else %}
                        var _params = {};
                        {% endif %}

                        // elaborate paging
                        var _count = {{ paginate_count_default }};
                        var _start = 0;
                        if ((params) && (params.count)) {
                            _count = params.count;
                        }
                        if ((params) && (params.start)) {
                            _start = params.start;
                        }
                        _params.start = _start;
                        _params.count = _count;
                        // elaborate filters
                        _params.filters = JSON.stringify({{ view_prefix }}get_filters_qsets());

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
                                var _data = data.json();
                                $$('{{ view_prefix }}datatable').view_count = _data.data.length;
                                $$('{{ view_prefix }}datatable').view_count_total = _data.total_count;
                                // counter
                                {{ view_prefix }}update_counter();
                                {% if is_enable_footer %}
                                    // footer only for first page
                                    for (var field_name in _data.footer) {
                                        var format = $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).footer[0].format;
                                        var format_col = $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).format;
                                        var text = _data.footer[field_name];
                                        if (format !== undefined){
                                            text = format(text)
                                        } else if(format_col !== undefined){
                                            text = format_col(text)
                                        }
                                        $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).footer[0].text = text;
                                        // adjust css of footer
                                        var css_col = $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).css;
                                        if($$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).footer[0].css === undefined){
                                            $$('{{ view_prefix }}datatable').getColumnConfig(field_name.replace('_footer', '')).footer[0].css = css_col;
                                        }
                                    }
                                    $$('{{ view_prefix }}datatable').refreshColumns();
                                {% endif %}
                                return data;
                            })
                            .fail(function (err) {
                            })
                            .finally(function (){
                            });
                }
            },
            {% else %}
            data: {{ view_prefix }}objects_list,
            {% endif %}
            navigation: true,
            checkboxRefresh: true,
            {% if is_enable_footer %}
            footer: true,
            {% endif %}
            on: {
                {% block datatable_on %}
                onCheck: function (row, column, state) {
                    {{ view_prefix }}update_counter();
                },
                {% if is_json_loading %}
                onBeforeFilter: function (id) {
                    if ({{ view_prefix }}_first_load==true) return false;
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
                    {%  if is_json_loading %}
                    if ({{ view_prefix }}_first_load==true) return false;
                    {%  endif %}
                    this.showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                },
                onAfterLoad: function () {
                    {% if not is_json_loading %}
                    $$('{{ view_prefix }}datatable').view_count = {{ view_prefix }}objects_list.length;
                    $$('{{ view_prefix }}datatable').view_count_total = {{ view_prefix }}objects_list.length;
                    {% else %}
                    $$('{{ view_prefix }}filter').setValue('0');
                    if ({{ view_prefix }}datatable_disable_savestate==false) {
                        {{ view_prefix }}save_state();
                    }
                    {% endif %}
                    {% if adjust_row_height %}
                    this.adjustRowHeight(); // for multirows
                    {% endif %}

                    this.hideOverlay();
                },
                onItemDblClick: function (id, e, trg) {
                    var el = $$('{{ view_prefix }}datatable').getSelectedItem();
                    {% block datatable_onitemdoubleclick %}
                    {% if is_enable_row_click and type_row_click == 'double' %}
                    {% if is_editable %}if (id.column != 'cmd_edit'){{% endif %}
                    load_js('{{ url_update|safe }}'.replace('0', el.{{column_id}}), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                    {% if is_editable %} } {{% endif %}
                    {% endif %}
                    {% endblock %}
                },
                onColumnResize: function (id,newWidth,oldWidth,user_action) {
                    if ({{ view_prefix }}datatable_disable_savestate==false) {
                        {{ view_prefix }}save_state();
                    }
                },
                onItemClick: function (id, e, trg) {
                    var el = $$('{{ view_prefix }}datatable').getSelectedItem();
                    {% block datatable_onitemclick %}
                    {% if is_editable %}
                    if (id.column == 'cmd_edit') {

                        to_close = {{ view_prefix }}edit_mode_id == id.row;
                        // send to server
                        if ({{ view_prefix }}edit_mode_id != undefined){
                            // TODO: send to server for validation
                            _params = el;
                            this.editStop();
                            load_js('{{ url_list|safe }}{% if '?' in url_list %}&{% else %}?{% endif %}update', undefined, undefined, 'POST', _params, undefined, 'json', abortAllPending=true);
                        }
                        // enable edit mode
                        if (({{ view_prefix }}edit_mode_id == undefined)||({{ view_prefix }}edit_mode_id != id.row)){
                            {{ view_prefix }}edit_mode_id = id.row;
                            this.editRow(id);
                        }
                        // close edit mode
                        if (to_close){
                            //this.undo();
                            this.editStop();
                            {{ view_prefix }}edit_mode_id = undefined;
                        }
                    }
                    {% endif %}
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
                        if (String(el.{{ layer.geofieldname }}_available).toLowerCase() == "true") {
                            $$("map").goToWebgisPk('{{layer.qxsname}}', '{{ pk_field_name }}', el.{{column_id}});
                        }
                    } else
                    {% endfor %}
                    {% endif %}
                    if (id.column == 'cmd_cp') {
                        {% block cmd_cp_click %}
                            {% if has_add_permission and is_enable_column_copy %}
                                load_js('{{ url_create|safe }}{% if '?' in url_create %}&{% else %}?{% endif %}pk_copy=' + el.{{column_id}}, undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                            {% endif %}
                        {% endblock %}
                    } else if (id.column == 'cmd_rm') {
                        {% block cmd_rm_click %}
                            {% if has_delete_permission and is_enable_column_delete %}
                                load_js('{{ url_delete|safe }}'.replace('0', el.{{column_id}}), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                            {% endif %}
                        {% endblock %}
                    } else if (id.column!='checkbox_action') {
                        {% block update_click %}
                            {% if is_enable_row_click %}
                                {% if is_editable %}if (id.column != 'cmd_edit'){{% endif %}
                                    {% if type_row_click == 'single' %}
                                    {% block update_url_call %}
                                    load_js('{{ url_update|safe }}'.replace('0', el.{{column_id}}), undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                                    {% endblock %}
                                    {% else %}
                                    webix.message({type: "success", text: "{{_("Double click to edit the element")|escapejs}}"});
                                    {% endif %}
                                {% if is_editable %} } {% endif %}
                            {% endif %}
                        {% endblock %}
                    }
                    {% endblock %}
                },
                {% endblock %}
            },
            {% block extra_datatable_options %}{% endblock %}
        }, 1);

        {% block footer %}
            {% if is_enable_footer %}
                {% if not is_json_loading %}
                    {% for field_name, field_value in footer.items %}
                        $$('{{ view_prefix }}datatable').getColumnConfig('{{ field_name }}'.replace('_footer', '')).footer[0].text = "{{ field_value }}"
                    {% endfor %}
                    $$('{{ view_prefix }}datatable').refreshColumns();
                {% endif %}
            {% endif %}
        {% endblock %}

        {% endblock %}

        {% block toolbar_list %}

        {% if model %}
        {% include "django_webix/include/actions_utils.js" %}

        {% block toolbar_list_actions %}
        {% include "django_webix/include/actions_list.js" %}
        {% endblock %}
        {% endif  %}

        {% include "django_webix/include/toolbar_list.js" %}
        {% endblock %}

        {%  if is_json_loading %}
        var {{ view_prefix }}initial_state = {{ view_prefix }}get_state_ui();
        // lock all data loading until here
        if ({{ view_prefix }}get_state()) {
           {{ view_prefix }}restore_state_grid();
        }

        {% block pre_json_load %}
        {% endblock %}

        setTimeout(function() {
            {{ view_prefix }}_first_load = false;
            {{ view_prefix }}apply_filters();
            {{ view_prefix }}datatable_disable_savestate = false; // dopo mettere nel after load
        },100) // build grid browser timing
        {% endif %}

    {% endif %}

{% endif %}

{% block extrajs_post %}{% endblock %}
{% endblock %}
