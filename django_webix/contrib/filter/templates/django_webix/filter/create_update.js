{% extends "django_webix/generic/create.js" %}
{% load static filtersmerger_utils %}

{% block extrajs_post %}
    {{ block.super }}

    {# Hide groups m2m if visibility is not restricted #}
    {% if object != None and object.insert_user == None %}
        $$("id_visibility").getParentView().hide();
        $$("id_assignees_groups").getParentView().hide();
    {% endif %}

    var checkVisibility = function(value) {
        if (value === "restricted") {
            $$("id_assignees_groups").getParentView().show();
            $$('{{ form.webix_id }}').config.rules['assignees_groups'] = webix.rules.isNotEmpty;
        } else {
            $$("id_assignees_groups").getParentView().hide();
            delete $$('{{ form.webix_id }}').config.rules['assignees_groups'];
        }
    }
    $$("id_visibility").attachEvent("onChange", function (newv, oldv) {
        checkVisibility(newv);
    });
    checkVisibility($$("id_visibility").getValue());

    {% if check_filter is not None %}
        var corrupted_filter = {% if check_filter %} true {% else %} false {% endif %};
        if (!corrupted_filter) {
            webix.alert({
                title: "{{_("Filter error")|escapejs}}",
                text: "{{_("There is a filter error, caused by a garment or model that is now non-existent or not correctly configured.")|escapejs}}"+
                "{{_("Unable to load filter, contact administrators to correct it")|escapejs}}.",
                type: "alert-error"
            });
        }
    {% endif %}

    $$('id_model').attachEvent('onChange', function () {
        webix.ui([], $$('querybuilder-container'));
        $$('querybuilder-container').addView({
            view: "jquery-querybuilder",
            id: "querybuilder",
            modelStart: $$('id_model').getValue(),
            filtersUrl: "{% url 'dwfilter.filter_config' app_label='app_label' model_name='model_name' %}",
            suggestUrl: "{% url 'dwfilter.suggest_exact' field='field' %}",
            limit_suggest: {{ limit_suggest }},
            webgis_enable: $$('map') != undefined,
            icons: {
                add_group: "fas fa-plus-circle",
                add_rule: "fas fa-plus",
                remove_group: "fas fa-times",
                remove_rule: "fas fa-times",
                error: "fas fa-exclamation-triangle"
            },
            plugins: {
                sortable: {
                    icon: "fas fa-sort"
                },
                'not-group': {}
            }
        });
    });


    var load_json = $$('json_loader_jqb').getValue();
    var model_name = $$('id_model').getValue();
    if (load_json !== null && load_json !== undefined && load_json !== '' && model_name !== null && model_name !== undefined && model_name !== '') {
        webix.ui([], $$('querybuilder-container'));
        $$('querybuilder-container').addView({
            view: "jquery-querybuilder",
            id: "querybuilder",
            modelStart: $$('id_model').getValue(),
            filtersUrl: "{% url 'dwfilter.filter_config' app_label='app_label' model_name='model_name' %}",
            suggestUrl: "{% url 'dwfilter.suggest_exact' field='field' %}",
            limit_suggest: {{ limit_suggest }},
            webgis_enable: $$('map') != undefined,
            icons: {
                add_group: "fas fa-plus-circle",
                add_rule: "fas fa-plus",
                remove_group: "fas fa-times",
                remove_rule: "fas fa-times",
                error: "fas fa-exclamation-triangle"
            },
            plugins: {
                sortable: {
                    icon: "fas fa-sort"
                },
                'not-group': {}
            }
        });
        $$('querybuilder').set_rules(JSON.parse(load_json));
    }

    if ($$('{{ form.webix_id }}_save') != undefined) {
        var save_click = $$('{{ form.webix_id }}_save').config.click
        $$('{{ form.webix_id }}_save').config.click = function () {
            var query = $$('querybuilder');
            if (query !== undefined) {
                var json_rules = $$('querybuilder').get_rules();
                if (json_rules !== undefined && json_rules !== null) {
                    $$('id_filter').setValue(JSON.stringify(json_rules));
                    save_click();
                }
            } else {
                webix.alert("{{_("You need to insert a filter before saving")|escapejs}}")
            }
        }
    }

    if ($$('{{ form.webix_id }}_save_continue') != undefined) {
        var save_continue_click = $$('{{ form.webix_id }}_save_continue').config.click
        $$('{{ form.webix_id }}_save_continue').config.click = function () {
            var query = $$('querybuilder');
            if (query !== undefined) {
                var json_rules = $$('querybuilder').get_rules();
                if (json_rules !== undefined && json_rules !== null) {
                    $$('id_filter').setValue(JSON.stringify(json_rules));
                    save_continue_click();
                }
            } else {
                webix.alert("{{_("You need to insert a filter before saving")|escapejs}}")
            }
        }
    }

    if ($$('{{ form.webix_id }}_save_addanother') != undefined) {
        var save_addother_click = $$('{{ form.webix_id }}_save_addanother').config.click
        $$('{{ form.webix_id }}_save_addanother').config.click = function () {
            var query = $$('querybuilder');
            if (query !== undefined) {
                var json_rules = $$('querybuilder').get_rules();
                if (json_rules !== undefined && json_rules !== null) {
                    $$('id_filter').setValue(JSON.stringify(json_rules));
                    save_addother_click();
                }
            } else {
                webix.alert("{{_("You need to insert a filter before saving")|escapejs}}")
            }
        }
    }

{% if is_popup %}
// TODO: da inserire anche un disattiva semplice
$$('main_toolbar_form').addView({
    id: 'otf_filter_apply',
    view: "tootipButton",
    type: "danger",
    align: "left",
    label: "{{_("Apply temporary filter")|escapejs}}",
    width: 200,
    click: function () {
        var query = $$('querybuilder');
        if (query !== undefined) {
            var json_rules = $$('querybuilder').get_rules();
            if (json_rules !== undefined && json_rules !== null) {
                var modello = $$('id_model').getValue();
                if (($$('main_content_right') != undefined) && ($$('main_content_right').getValue() == 'webgis_leaflet') && ($$('map') != undefined)) {
                    // Webgis
                    var active_layer = $$('map').activeLayer;
                    if (active_layer != undefined) {
                        if (active_layer.properties.djangoApp != undefined && active_layer.properties.djangoModel != undefined) {
                            var layer_name = active_layer.name;
                            if (otf_filter[modello] == undefined) {
                                otf_filter[modello] = {}
                                otf_filter[modello][layer_name] = {
                                    'active': true,
                                    'json': json_rules
                                }
                            }else{
                                otf_filter[modello][layer_name] = {
                                    'active': true,
                                    'json': json_rules
                                }
                            }
                            $$('map').setDjangoWebixOTFFilters(active_layer, true);
                            $$('map').setWmsFilterParams(active_layer);
                        }
                    }
                } else {
                    // Lista
                    if (otf_filter[modello] !== undefined) {
                        otf_filter[modello]['list'] = {
                            'active': true,
                            'json': json_rules
                        }
                    } else {
                        otf_filter[modello] = {
                            'list': {
                                'active': true,
                                'json': json_rules
                            }
                        }
                    }
                    {% with param='DjangoAdvancedOTFWebixFilter'|request_filter_param %}
                    {% if param %}
                    setWebixFilter(modello, '{{ param }}', JSON.stringify(otf_filter[modello]['list']['json']));
                    {% endif %}
                    {% endwith %}
                    if ($$(modello.split('.').join('_') + '_datatable') != undefined) {
                        window[modello.split('.').join('_') + '_apply_filters']();
                    }
                }
            }
            load_js("{{ url_list }}");
        } else {
            webix.alert("{{_("You need to insert a filter before saving")|escapejs}}")
        }
    }
}, $$('main_toolbar_form').getChildViews().length - 1)

if($$("{{ view_prefix }}filter_status") != undefined){
    $$("{{ view_prefix }}filter_status").hide();
}
{% endif %}
{% endblock %}
