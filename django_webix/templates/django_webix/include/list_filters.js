{% load django_webix_utils static i18n filtersmerger_utils %}

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
                        filter_txt = filter_txt.replace(',','.')
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
                    } else {
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

function {{ view_prefix }}is_active_otf_filter() {
    var key = '{{ model_name }}';
    if (typeof otf_filter !== "undefined") {
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

function {{ view_prefix }}is_present_otf_filter() {
    var key = '{{ model_name }}';
    if (typeof otf_filter !== "undefined") {
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

function {{ view_prefix }}get_otf_filter() {
    var key = '{{ model_name }}';
    if (typeof otf_filter !== "undefined") {
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

function {{ view_prefix }}deactivate_otf_filter() {
    var key = '{{ model_name }}';
    if (typeof otf_filter !== "undefined") {
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
    if ({{ view_prefix }}is_active_otf_filter()) {
        extra = '+';
    }
    var advanced_filter_count = '0';
    {% with param='DjangoAdvancedWebixFilter'|request_filter_param %}
    {% if param and model_name %}
    var waf = webixAppliedFilters['{{ model_name }}'];
    if (waf!=undefined) {
        var advanced_filter = waf['{{ param }}'];
        if (advanced_filter) {
            advanced_filter_count = advanced_filter.split(',').length
        }
    }
    {% endif %}
    {% endwith %}
    if (extra != '' && advanced_filter_count == '0') {
        advanced_filter_count = '';
    }
    $('#{{ view_prefix }}django_webix_filter_counter').text(advanced_filter_count + extra);
    $$('{{ view_prefix }}filter').setValue('1');
    $$('{{ view_prefix }}datatable').filterByAll();
}

function {{ view_prefix }}remove_filters() {
    {{ view_prefix }}restore_initial_state();
    {{ view_prefix }}restore_state_grid();
    {{ view_prefix }}apply_filters();
}
