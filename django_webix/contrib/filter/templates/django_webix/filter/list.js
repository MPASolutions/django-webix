{% extends "django_webix/generic/list.js" %}
{% load static django_webix_utils filtersmerger_utils %}

{% block context_cleaner %}
    {% if not is_popup %}
        {{ block.super }}
    {% endif %}
{% endblock %}

{% block toolbar_navigation %}
    {% if is_popup %}
        function popup_query_builder_close() {
            webix.fullscreen.exit();
            $$('popup_query_builder').destructor();
        }

        if ($$('popup_query_builder') == undefined) {
            webix.ui({
                id: 'popup_query_builder',
                view: "window",
                height: 500,
                width: 1100,
                modal: true,
                move: true,
                resize: true,
                position: "center",
                head: {
                    view: "toolbar",
                    cols: [
                        {
                            id: "{{ view_prefix }}filter_status",
                            view: "switch",
                            onLabel: "{{_("No")|escapejs}}",
                            offLabel: "{{_("Yes")|escapejs}}",
                            labelWidth: 140,
                            value: 0,
                            width: 210,
                            label: "{{_("Show active only")|escapejs}}",
                            on:{
                                onChange: function(newValue, oldValue, config){
                                    $$('{{ view_prefix }}datatable').filterByAll();
                                    $('input[name="{{ view_prefix }}master_checkbox"]').hide();
                                }
                            }
                        },
                        {view: "label", label: "<b>{{_("Advanced filters")|escapejs}}</b>", type: "header", css: {'text-align': 'center'}},
                        {% block toolbar %}
                        {
                            view: "toggle",
                            offLabel: "Fullscreen",
                            onLabel: "Fullscreen",
                            width: 100,
                            align: 'right',
                            click: function (id, event) {
                                if (this.getValue())
                                    webix.fullscreen.exit();
                                else
                                    webix.fullscreen.set("popup_query_builder");
                            }
                        },
                        {
                            view: "button",
                            label: '{{_("Close")|escapejs}}',
                            width: 100,
                            align: 'right',
                            type: 'form',
                            click: "popup_query_builder_close();"
                        },
                        {% endblock %}
                    ]
                },
                body: {
                    id: 'content_query_builder',
                    rows: []
                }
            }).show();
        } else {
            webix.ui([], $$("content_query_builder"));
        }
    {% endif %}

    {{ block.super }}

{% endblock %}

{% block extrajs_post %}{{ block.super }}

    {# modifica di datatable e di grafica #}
    $$('{{ view_prefix }}datatable').define('scheme', {
        $change: function (item) {
            if (item.checkbox_action)
                item.$css = {'background-color': '#34ae60', 'color': 'white'};
            else
                item.$css = {}
        }
    });

    {# per togliere il titolo senza rompere tutto  #}
    $$('{{ view_prefix }}main_toolbar_navigation').hide();
    $$("{{ view_prefix }}_addnew").define('label', "{{_("Create new filter")|escapejs}}"); {# ha deciso leo su crea #}
    $$("{{ view_prefix }}_addnew").refresh();
    $$('{{ view_prefix }}datatable').showColumn("checkbox_action");

    // azione sul check dei filtri salvati
    $$('{{ view_prefix }}datatable').attachEvent('onCheck', function () {
        var ids = [];
        $$("{{ view_prefix }}datatable").eachRow(function (id) {
            if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
                ids.push(id);
            }
        });

        // webgis -- funziona
        if (($$('main_content_right') != undefined) && ($$('main_content_right').getValue() == 'webgis_leaflet')) {
            $$('map').setDjangoWebixFilters($$('map').activeLayer, ids); // TODO: fix map
            $$('map').setWmsFilterParams($$('map').activeLayer);
        }
        else{
            {# the toString is needed so it do not send an array but a comma separated string #}
            {% if list_view_prefix %}
                var model = '{{ list_view_prefix }}'.split('_').slice(0, 2).join('.');
                {% with param='DjangoAdvancedWebixFilter'|request_filter_param %}
                    {% if param %}
                        setWebixFilter(model, "{{ param }}", ids.toString());
                    {% endif %}
                {% endwith %}
            {{ list_view_prefix }}apply_filters();
            {% endif %}
        }
    });

    // set filters ids selected from previus selection
    if (($$('main_content_right') != undefined) && ($$('main_content_right').getValue() == 'webgis_leaflet')) {
        // if called from webig
        var layerItem = $$('map').overlayLayers[$$('map').activeLayer.name]; // TODO: fix map
        $.each(layerItem.filters.advanced, function (index, value) {
            var item = $$('{{ view_prefix }}datatable').getItem(value);
            item["status"] = 1;
            item.checkbox_action = 1;
            $$('{{ view_prefix }}datatable').updateItem(value, item);
        });
    } else {
        // if called from list
        {% if list_view_prefix %}
        var model = '{{ list_view_prefix }}'.split('_').slice(0, 2).join('.');
        if(model in webixAppliedFilters){
            {% with param='DjangoAdvancedWebixFilter'|request_filter_param %}
                {% if param %}
                    if (webixAppliedFilters[model]['{{ param }}'] != null) {
                        $.each(webixAppliedFilters[model].ADVANCEDFILTER.split(','),
                            function (index, value) {
                                if(value != undefined && value != '') {
                                    var item = $$('{{ view_prefix }}datatable').getItem(value);
                                    item["status"] = 1;
                                    item.checkbox_action = 1;
                                    $$('{{ view_prefix }}datatable').updateItem(value, item);
                                }
                            });
                    }
                {% endif %}
            {% endwith %}
        }
        {% endif %}
    }

    var config_check = {% if config_check %}true{% else %}false{% endif %};
    if (!config_check) {
        webix.alert({
            title: "{{_("Configuration error")|escapejs}}",
            text: "{{_("ATTENTION: there is a filter application configuration error. Contact administrators.")|escapejs}}",
            type: "alert-error"
        });
        webix.ui([], $$("{{ webix_container_id }}"));
    }

    // OTF filter
    if (($$('main_content_right') != undefined) && ($$('main_content_right').getValue() == 'webgis_leaflet') &&
        ($$('map') != undefined) && otf_filter != undefined) {

        // called from webig
        var layerItem = $$('map').overlayLayers[$$('map').activeLayer.name];
        var active_layer = $$('map').activeLayer;
        var json_filter = $$('map').getDjangoWebixOTFFilters($$('map').activeLayer);
        var model_name = active_layer.properties.djangoApp + '.' + active_layer.properties.djangoModel;

        if(otf_filter[model_name] != undefined){
            if(otf_filter[model_name][active_layer.name] != undefined){
                if (otf_filter[model_name][active_layer.name]['json'] != undefined) {
                    $$('{{ webix_container_id }}_toolbar').addView({
                        id: 'otf_fiter_reload',
                        view: "tootipButton",
                        align: "left",
                        label: "{{_("Change temporary filter")|escapejs}}",
                        width: 150,
                        click: function () {
                            var o_filter = otf_filter[model_name][active_layer.name]['json'];
                            if (o_filter != undefined) {
                                var data = {
                                    'SEND_INITIAL_DATA': true,
                                    'filter': JSON.stringify(o_filter),
                                    'model': model_name
                                };
                                load_js('{{ url_create }}', undefined, undefined, 'POST', data, undefined, undefined, abortAllPending = true);
                            } else {
                                webix.alert('{{_("Invalid filter")|escapejs}}');
                            }
                        }
                    }, 0);

                    $$('{{ webix_container_id }}_toolbar').addView({
                        id: 'otf_fiter_deactivate',
                        view: "tootipButton",
                        align: "left",
                        label: "{{_("Disable temporary filter")|escapejs}}",
                        width: 150,
                        click: function () {
                            otf_filter[model_name][active_layer.name]['active'] = false;
                            $$('map').setDjangoWebixOTFFilters(active_layer, false);
                            $$('map').setWmsFilterParams(active_layer);
                            this.disable();
                        }
                    }, 1);
                    if (!layerItem.filters.otf) {
                        $$('otf_fiter_deactivate').disable();
                    }
                }
            }
        }
    }else {
        {% if list_view_prefix %}
            if (typeof {{ list_view_prefix }}is_present_otf_filter != 'undefined' && {{ list_view_prefix }}is_present_otf_filter()) {
                $$('{{ webix_container_id }}_toolbar').addView({
                    id: 'otf_fiter_reload',
                    view: "tootipButton",
                    align: "left",
                    label: "{{_('Change temporary filter')|escapejs}}",
                    width: 150,
                    click: function () {
                        var model = '{{ list_view_prefix }}'.split('_').slice(0, 2).join('.');
                        var otf_filter = {{ list_view_prefix }}get_otf_filter();
                        if(otf_filter != undefined) {
                            var data = {
                                'SEND_INITIAL_DATA': true,
                                'filter': JSON.stringify(otf_filter),
                                'model': model
                            };
                            load_js('{{ url_create }}', undefined, undefined, 'POST', data, undefined, undefined, abortAllPending = true);
                        }else{
                            webix.alert('{{_("Invalid filter")|escapejs}}');
                        }
                    }
                }, 0);

                $$('{{ webix_container_id }}_toolbar').addView({
                    id: 'otf_fiter_deactivate',
                    view: "tootipButton",
                    align: "left",
                    label: "{{_('Disable temporary filter')|escapejs}}",
                    width: 150,
                    click: function () {
                        {{ list_view_prefix }}deactivate_otf_filter();
                        {% with param='DjangoAdvancedOTFWebixFilter'|request_filter_param %}
                            {% if param %}
                              setWebixFilter(model, '{{ param }}', null);
                            {% endif %}
                        {% endwith %}
                        {{ list_view_prefix }}apply_filters();
                        this.disable();
                    }
                }, 1);

                if (!{{ list_view_prefix }}is_active_otf_filter()) {
                    $$('otf_fiter_deactivate').disable();
                }
            }
        {% endif %}
    }


    {% if is_popup %}
    $$('{{ view_prefix }}datatable').registerFilter(
        $$("{{ view_prefix }}filter_status"),
        {
            columnId: "checkbox_action"
        },
        {
            getValue:function(view){
              return view.getValue();
            },
            setValue:function(view, value){
              view.setValue(value)
            }
        }
    );
    $('input[name="{{ view_prefix }}master_checkbox"]').hide();
    if($$("{{ view_prefix }}filter_status") != undefined){
        $$("{{ view_prefix }}filter_status").show();
    }
    {% endif %}

{% endblock %}
