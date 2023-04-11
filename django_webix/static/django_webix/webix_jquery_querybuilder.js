webix.ui.jQueryQuerybuilder = webix.protoUI({
    name: "jquery-querybuilder",
    defaults: {
        plugins: [],
        default_filter: null,
        sort_filters: false,
        allow_groups: true,
        allow_empty: false,
        display_errors: true,
        conditions: ['AND', 'OR'],
        default_condition: 'AND',
        inputs_separator: ' , ',
        display_empty_filter: true,
        select_placeholder: '------',
        lang_code: 'en',
        webgis_enable: false,
        icons: {
            add_group: "glyphicon glyphicon-plus-sign",
            add_rule: "glyphicon glyphicon-plus",
            remove_group: "glyphicon glyphicon-remove",
            remove_rule: "glyphicon glyphicon-remove",
            error: "glyphicon glyphicon-warning-sign"
        }
    },
    $init: function (config) {
        this._contentObj = this.$view.firstChild;
        this.queryBuilder = null;

        this.attachEvent("onTouchStart", function(current_view, prev_view){
            // console.log("onTouchStart")
        });
    },
    $getSize: function(x, y){
        if (this.queryBuilder !== undefined && this.queryBuilder !== null) {
            var elements = this.queryBuilder.$el.children();
            // x = elements.width()
            y = elements.outerHeight(true)
        }
        return webix.ui.template.prototype.$getSize.call(this, x, y+ 30);
    },
    $setSize: function(x, y){
        if (this.queryBuilder !== undefined && this.queryBuilder !== null) {
            var elements = this.queryBuilder.$el.children();
            // x = elements.outerWidth(true)
            y = elements.outerHeight(true)
        }

        webix.ui.template.prototype.$setSize.call(this, x, y + 30);
        if (webix.ui.view.prototype.$setSize.call(this, x, y + 30)) {
            //custom logic
        }
    },
    render: function () {
        this.callEvent("onBeforeRender", []);
        var queryBuilderOptions = {
            // Options
            default_filter: this.config.default_filter,
            sort_filters: this.config.sort_filters,
            allow_groups: this.config.allow_groups,
            allow_empty: this.config.allow_empty,
            display_errors: this.config.display_errors,
            conditions: this.config.conditions,
            default_condition: this.config.default_condition,
            inputs_separator: this.config.inputs_separator,
            display_empty_filter: this.config.display_empty_filter,
            select_placeholder: this.config.select_placeholder,
            lang_code: this.config.lang_code,
            icons: this.config.icons,
            // Configuration
            plugins: this.config.plugins,
            rules: this.config.rules,
            templates: {
                rule: '\
                    <div id="{{= it.rule_id }}" class="rule-container"> \
                        <div class="rule-header"> \
                            <div class="btn-group pull-right rule-actions"> \
                                <button type="button" class="btn btn-xs btn-danger" data-delete="rule"> \
                                    <i class="{{= it.icons.remove_rule }}"></i> {{= it.translate("delete_rule") }} \
                                </button> \
                            </div> \
                        </div> \
                        {{? it.settings.display_errors }} \
                            <div class="error-container"><i class="{{= it.icons.error }}"></i></div> \
                        {{?}} \
                        <div class="rule-filter-container"></div> \
                        <div></div> \
                        <div class="rule-operator-container"></div> \
                        <div class="rule-value-container"></div> \
                    </div>'
            }
        };

        if (this.config.modelStart === undefined) throw Error("modelStart is required to use queryBuilder");
        if (this.config.filtersUrl === undefined) throw Error("filtersUrl is required to use queryBuilder");

        var model = this.config.modelStart.split(".");

        // Wait download config
        var xhr = webix.ajax().sync().get(this.config.filtersUrl.replace("app_label", model[0]).replace("model_name", model[1]));
        var json = JSON.parse(xhr.response);

        var availableTypes = ["string", "integer", "double", "date", "time", "datetime", "boolean"]

        var fields = [];
        json['fields'].forEach(function (b, index, array) {
            var type = b['type'];
            if (availableTypes.indexOf(type) < 0)
                type = "string";
            var field = {id: b['id'], label: b['label'], type: type, operators: b['operators'], follow: true, model: json['model']};

            field['follow'] = ('follow' in b) ? b['follow'] : false;
            field['follow_model'] = ('follow_model' in b) ? b['follow_model'] : null;
            if ('input' in b)
                field['input'] = b['input']
            if ('values' in b)
                field['values'] = b['values']
            if ('plugin' in b)
                field['plugin'] = b['plugin']
            if ('plugin_webix' in b)
                field['plugin_webix'] = b['plugin_webix']
            if ('plugin_config' in b)
                field['plugin_config'] = b['plugin_config']
            if ('value_separator' in b)
                field['value_separator'] = b['value_separator']
            if ('webix_type' in b)
                field['webix_type'] = b['webix_type']
            else
                field['webix_type'] = 'string'
            fields.push(field);
        })

        var operators = [];
        json['operators'].forEach(function (a, index, array) {
            var oper = {
              type: a.name,
              nb_inputs: a.nb_inputs,
              multiple: a.multiple,
              label: a.label,
              pick_geometry: a.pick_geometry,
              apply_to: ["string", "number", "datetime", "boolean"]
            }
            if ('values' in a){
                oper['values'] = a.values
            }
            operators.push(oper);
        });
        queryBuilderOptions["operators"] = operators
        queryBuilderOptions["filters"] =  fields

        // Create queryBuilder
        $(this._contentObj).queryBuilder(queryBuilderOptions);

        // Set queryBuilder public
        this.queryBuilder = $(this._contentObj)[0].queryBuilder;
        this.queryBuilder.filtersUrl = this.config.filtersUrl;
        this.queryBuilder.modelStart = this.config.modelStart;
        this.queryBuilder.suggestUrl = this.config.suggestUrl;
        this.queryBuilder.limit_suggest = this.config.limit_suggest;
        this.queryBuilder.webgis_enable = this.config.webgis_enable;

        this.callEvent("onAfterRender", []);
        this._setEvents();
        this.queryBuilder.model.root.drop();
        this.queryBuilder.setRoot(true);
    },
    _setEvents: function () {
        this.queryBuilder.on('afterInit.queryBuilder', function (e, rule) {});

        this.queryBuilder.on('afterAddGroup.queryBuilder', function(e, group) {
            // console.log('afterAddGroup');
            var container = group.$el.find(".group-actions");
            var addRuleButton = group.$el.find("button[data-add='rule']");
            var addGroupButton = group.$el.find("button[data-add='group']");
            var deleteGroupButton = group.$el.find("button[data-delete='group']");
            var is_root = (deleteGroupButton.html() !== undefined);
            container.empty();

            var layout_webix = {
                cols: [
                    {
                        id: "button_add_rule_" + group.id,
                        view: "button",
                        value: addRuleButton.html(),
                        autowidth: true
                    },
                    {
                        id: "button_add_group_" + group.id,
                        view: "button",
                        value: addGroupButton.html(),
                        autowidth: true
                    }
                ]
            }

            if (is_root !== false) {
                layout_webix.cols.push(
                    {
                        id: "button_delete_group_" + group.id,
                        view: "button",
                        value: deleteGroupButton.html(),
                        css: "webix_danger",
                        autowidth: true
                    }
                );
            }

            if($$("button_add_rule_" + group.id) != undefined){
                $$("button_add_rule_" + group.id).destructor();
            }

            if($$("button_add_group_" + group.id) != undefined){
                $$("button_add_group_" + group.id).destructor();
            }

            container.webix_layout(layout_webix);

            $$("button_add_rule_" + group.id).getInputNode().setAttribute("data-add", "rule");
            $$("button_add_group_" + group.id).getInputNode().setAttribute("data-add", "group");

            if (is_root !== false) {
                $$("button_delete_group_" + group.id).getInputNode().setAttribute("data-delete", "group");
            }

            // Change Conditions
            container = group.$el.find(".group-conditions");
            // var notGroupButton = container.$el.find("button[data-not='group']");

            var andOrConditions = container.find("input[type='radio']");
            var notGroupButton = container.find("button[data-not='group']");

            container.find('label').hide();
            notGroupButton.hide();
            andOrConditions.hide()

            var options = [];
            andOrConditions.each(function () {
                options.push({id: $(this).val(), value: $(this).parent('label').text().trim()})
            });

            var layout_conditions = {
                cols: [
                    {
                        view: "checkbox",
                        id: "not_" + group.id,
                        label: 'NOT',
                        labelWidth: 50,
                        width: 100,
                        on: {
                            onChange: function (newv, oldv) {
                                var val = true;
                                if(newv === 0){
                                    val = false;
                                }
                                if(group.not !== val) {
                                    notGroupButton.trigger('click');
                                }
                            }
                        }
                    },
                    {
                        view: 'segmented',
                        id: "cond_" + group.id,
                        options: options,
                        width: 200,
                        on: {
                            onChange: function (newv, oldv) {
                                andOrConditions.filter('[value=' + newv + ']').prop('checked', true);
                                andOrConditions.trigger("change");
                            }
                        }
                    }
                ]
            }

            if($$("not_" + group.id) != undefined){
                $$("not_" + group.id).destructor();
            }
            if($$("cond_" + group.id) != undefined){
                $$("cond_" + group.id).destructor();
            }

            container.webix_layout(layout_conditions);
            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                    $$(view_id).resize();
                }
            }
        });
        this.queryBuilder.on('afterAddRule.queryBuilder', function(e, rule) {
            // console.log('afterAddRule');
            var container = rule.$el.find(".rule-actions");
            var deleteButton = rule.$el.find("button[data-delete='rule']");
            container.empty();
            if($$("button_" + rule.id) != undefined){
                $$("button_" + rule.id).destructor();
            }
            container.webix_button({
                id: "button_" + rule.id,
                view: "button",
                value: deleteButton.html(),
                css: "webix_danger",
                autowidth: true
            });
            $$("button_" + rule.id).getInputNode().setAttribute("data-delete", "rule");
            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                    $$(view_id).resize();
                }
            }
        });

        this.queryBuilder.on('afterCreateRuleFilters.queryBuilder', function (e, rule) {
            // console.log('afterCreateRuleFilters')
            var container = rule.$el.find(".rule-filter-container");
            var filterSelect = rule.$el.find("select[name='" + rule.id + "_filter']");
            filterSelect.hide();
            var model_base = this.queryBuilder.modelStart;

            var options = [];
            filterSelect.find("option").each(function() {
                if ($(this).val() == "-1") {
                    options.push({id: $(this).val(), value: $(this).text(), $empty: true});
                    return;
                }
                var model = $(this).val().split('.');
                model = model[0] + '.' + model[1];
                if (model == model_base) {
                    options.push({id: $(this).val(), value: $(this).text()});
                }
            });

            if($$("filter_" + rule.id) != undefined){
                $$("filter_" + rule.id).destructor();
            }

            container.webix_combo({
                id: "filter_" + rule.id,
                options: options,
                label: 'Campo',
                labelWidth: 100,
                width: 300,
                css: {"float": "left"},
                rule_id: rule.id,
                on: {
                    onChange: function (newv, oldv) {
                        var rule_id = this.config.rule_id;
                        var my_id = this.config.id;
                        var posfix = '';
                        var next = false;
                        var my_number = 0;
                        var comps = my_id.split('__')
                        if(comps.length > 1){
                            my_number = parseInt(comps[1]);
                            posfix = '__' + comps[1];
                            next = true;
                        }
                        var selectors = rule.$el.find("select[name^='" + rule_id + "_filter']")
                        if (selectors.length > 1 && next == true) { //quasi di sicuro sono sempre entrambe vere
                            for (var i = 0; i < selectors.length; i++) {
                                var names = selectors[i].name.split('__')
                                if (names.length > 1) {
                                    //significa che abbiamo preso uno che è nella forma __[n]
                                    //controllo se il suo __[n] è maggiore
                                    if (parseInt(names[1]) > my_number) {
                                        //delete dell'elemento
                                        rule.$el.find("select[name='" + selectors[i].name + "']").remove()
                                        $$("filter_" + rule_id + "__" + names[1]).destructor()
                                    }
                                } else {
                                    //delete dell'elemento
                                    rule.$el.find("select[name='" + selectors[i].name + "']").remove()
                                    $$("filter_" + rule_id).destructor()
                                }
                            }
                            //cambio il mio id e il name dell'oggetto jqb
                            var old_id = this.config.id;
                            this.id_setter('filter_' + rule_id); //webix component
                            this.config.id = 'filter_' + rule_id; //webix component
                            if (webix.ui.views[old_id] != undefined) {
                                delete webix.ui.views[old_id];
                            }
                            var my_rule_select = rule.$el.find("select[name^='" + rule_id + "_filter" + posfix + "']");
                            my_rule_select[0].name = my_rule_select[0].name.split('__')[0];
                        }
                        // da cambiare di nuovo tutti gli id superiori al mio .... come li prendo ?
                        // var selector = selectors[0]
                        // NB: non servirà più il posfix che tanto non ci sarà più
                        selectors = rule.$el.find("select[name='" + rule_id + "_filter']")
                        selectors.val(newv || "-1");
                        selectors.trigger("change");
                    }
                }
            });
            $('[view_id=filter_' + rule.id + ']').css("z-index", "1100");
        });

        this.queryBuilder.on('afterCreateRuleOperators.queryBuilder', function (e, rule) {
            // console.log('afterCreateRuleOperators');
            var query = this.queryBuilder;
            var container = rule.$el.find(".rule-operator-container");
            if(container.find("span").length > 0){
                container.find("span").remove();
            }
            var operatorSelect = rule.$el.find("select[name='" + rule.id + "_operator']");
            var operator_selected = operatorSelect.val();
            operatorSelect.hide();

            var options = [];
            operatorSelect.find("option").each(function() {
                var operator_id = $(this).val();
                var operator_label = $(this).text()
                query.operators.forEach(function (a, index, array) {
                    if(a.type == operator_id){
                        operator_label = a.label;
                    }
                });
                options.push({id: operator_id, value: operator_label});
            });

            if($$("operator_" + rule.id) != undefined) {
                $$("operator_" + rule.id).destructor();
            }

            container.webix_combo({
                id: "operator_" + rule.id,
                options: options,
                css: {'margin-left': '20px'},
                label: 'Operatore',
                labelWidth: 100,
                width: 300,
                value: operator_selected,
                on: {
                    onChange: function (newv, oldv) {
                        operatorSelect.val(newv);
                        operatorSelect.trigger("change");
                    }
                }
            });
            $('[view_id=operator_' + rule.id + ']').css("z-index", "1100");

            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                }
            }
        });
        this.queryBuilder.on('afterCreateRuleInput.queryBuilder', function (e, rule) {
            // console.log('afterCreateRuleInput');
            var query = this.queryBuilder
            var container = rule.$el.find(".rule-value-container");
            var ruleInputs = rule.$el.find("input[name^='" + rule.id + "_value']");
            var ruleInputsSelect = rule.$el.find("select[name^='" + rule.id + "_value']");
            if (ruleInputsSelect.length > 0) {
                ruleInputsSelect.hide();
                var input_value = ruleInputsSelect.val();
                var options = [];
                if(ruleInputsSelect.find("option").length == 0){
                    for( [key, value] of Object.entries(rule.filter.values) ){
                        ruleInputsSelect.append(
                          $('<option/>').attr('value', key).text(value)
                        );
                    }
                }
                ruleInputsSelect.find("option").each(function() {
                    options.push({id: $(this).val(), value: $(this).text()})
                });
                if ($$('value_' + ruleInputsSelect.attr("name")) != undefined) {
                    $$('value_' + ruleInputsSelect.attr("name")).destructor();
                }
                container.webix_combo({
                    id: 'value_' + ruleInputsSelect.attr("name"),
                    options: options,
                    width: 200,
                    value: input_value,
                    on: {
                        onChange: function (newv, oldv) {
                            ruleInputsSelect.val(newv);
                            ruleInputsSelect.trigger("change");
                        }
                    }
                });
                $('[view_id=' + 'value_' + ruleInputsSelect.attr("name") + ']').css("z-index", "1100");
            }
            if(ruleInputs.length > 0) {
                ruleInputs.each(function () {
                    var ruleInput = $(this);
                    var input_value = ruleInput.val();
                    var type = rule.filter.webix_type;
                    ruleInput.hide();
                    if ($$('value_' + ruleInput.attr("name")) != undefined) {
                        $$('value_' + ruleInput.attr("name")).destructor();
                    }
                    if (rule.operator.values !== undefined && rule.operator.values !== null){
                        var options = [];

                        for([key, value] of Object.entries(rule.operator.values)){
                            options.push({id: key, value: value})
                        }
                        container.webix_select({
                            id: 'value_' + ruleInput.attr("name"),
                            options: options,
                            width: 300,
                            on: {
                                onChange: function (newv, oldv) {
                                    ruleInput.val(newv);
                                    ruleInput.trigger("change");
                                }
                            }
                        });
                        $$('value_' + ruleInput.attr("name")).callEvent('onchange');
                        $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                    }
                    else {
                        if (type === 'date') {
                            container.webix_datepicker({
                                id: 'value_' + ruleInput.attr("name"),
                                width: 300,
                                format: webix.Date.dateToStr("%Y-%m-%d"),
                                on: {
                                    onChange: function (newv, oldv) {
                                        var format_giorno_js = webix.Date.dateToStr("%Y-%m-%d");
                                        ruleInput.val(format_giorno_js(newv));
                                        ruleInput.trigger("change");
                                    }
                                }
                            });
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        } else if (type === 'time') {
                            container.webix_datepicker({
                                id: 'value_' +  ruleInput.attr("name"),
                                width: 300,
                                type: "time",
                                format: webix.Date.dateToStr("%H:%i:%s"),
                                on: {
                                    onChange: function (newv, oldv) {
                                        var format_ora_js = webix.Date.dateToStr("%H:%i:%s")
                                        ruleInput.val(format_ora_js(newv));
                                        ruleInput.trigger("change");
                                    }
                                }
                            });
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        }
                        else {
                            var webix_field = {
                                id: 'value_' + ruleInput.attr("name"),
                                width: 300,
                                on: {
                                    onChange: function (newv, oldv) {
                                        var val = newv
                                        if(this.config.regex != undefined) {
                                            if (!this.config.regex.test(newv)) {
                                                if (oldv == null || oldv == undefined) {
                                                    oldv = 0
                                                }
                                                val = oldv
                                                this.setValue(oldv);
                                            }
                                        }
                                        if (Array.isArray(val)) {
                                            ruleInput.val(val.join(rule.filter.value_separator));
                                        } else {
                                            ruleInput.val(val);
                                        }
                                        ruleInput.trigger("change");
                                        $$('querybuilder-container').resize();

                                        if(this.config.view == 'multicombo'){
                                            var values_set = this.getValue();
                                            var suggestion = [];
                                            values_set.split(rule.filter.value_separator).forEach(function (a, index, array) {
                                                suggestion.push({'id': a, 'value':a});
                                            })
                                            this.getList().parse(suggestion);
                                        }
                                    },
                                    onFocus: function(current_view, prev_view){
                                        if(this.config.suggest != undefined && this.config.suggest != null) {
                                            var suggest = $$(this.config.suggest);
                                            var l = suggest.getList();
                                            if(l.config.dataFeed != undefined && l.config.dataFeed != null) {
                                                suggest.show(this.getInputNode());
                                                l.load(l.config.dataFeed);
                                            }
                                        }
                                    }
                                }
                            }
                            var operator_selected = rule.operator.type;
                            if (type == 'integer') {
                                if (operator_selected === 'in') {
                                    // non reve piu
                                    // webix_field.regex = new RegExp('\^((-{0,1}\\d*)' + rule.filter.value_separator + '{0,1})*\$');
                                } else {
                                    webix_field.regex = new RegExp('\^-{0,1}\\d*\$');
                                }
                            }
                            if (type == 'double') {
                                if (operator_selected === 'in') {
                                    // non reve piu
                                    // webix_field.regex = new RegExp('\^((\\d+\(\\.\\d+\)\?)' + rule.filter.value_separator + '{0,1})*\$');
                                } else {
                                    webix_field.regex = new RegExp('\^\\d+\(\\.\\d+\)\?\$');
                                }
                            }
                            var rule_values = null;
                            if(rule.filter.values != undefined && rule.filter.values.length > 0) {
                                rule_values = [];
                                rule.filter.values.forEach(function (l, i) {
                                    for (var k in l) {
                                        rule_values.push({id: k, value: l[k]})
                                    }
                                })
                            }
                            if(rule.operator.multiple === true){
                                var suggest_multi;
                                if(rule_values != null){
                                    suggest_multi = rule_values;
                                } else {
                                    suggest_multi = {
                                        dynamic: true,
                                        body: {
                                            data: [],
                                            dataFeed: query.suggestUrl.replace('field', rule.filter.id) + '?limit=' + query.limit_suggest
                                        }
                                    };
                                }
                                webix_field.suggest = suggest_multi;
                                webix_field.separator = ";";
                                container.webix_multicombo(webix_field);
                            } else if(rule.operator.pick_geometry === true){
                                webix_field.disabled = query.webgis_enable;
                                webix_field.width = 300;
                                if (query.webgis_enable) {
                                    var layers = $$('map').getLayersFromModel(rule.filter.model);
                                    var options_geo = [];
                                    layers.forEach(function (l, i) {
                                        if($$('map').overlayLayers[l.id].filters.spatial.length > 0){
                                            options_geo.push(l);
                                        }
                                    });
                                    var label_combo = 'Scegliere un layer WebGIS filtrato:';
                                    if (options_geo.length == 0) {
                                        label_combo = 'Nessn layer filtrato nel WebGIS';
                                    }
                                    container.webix_combo({
                                        id: 'value_' + ruleInput.attr("name") + '_geo_pick',
                                        view: 'combo',
                                        options: options_geo,
                                        width: 300,
                                        value: null,
                                        label: label_combo,
                                        labelPosition: 'top',
                                        on: {
                                            onChange: function (newv, oldv) {
                                                if (newv != null && newv !== '') {
                                                    var filter = $$('map').overlayLayers[newv].filters.spatial[0];
                                                    var id_input = this.config.id.replace('_geo_pick', '');
                                                    $$(id_input).setValue(filter);
                                                }
                                            }
                                        }
                                    });
                                }
                                container.webix_text(webix_field);
                            } else if(rule_values != null){
                                webix_field.options = rule_values;
                                container.webix_combo(webix_field);
                            } else {
                                if (rule.operator.type == 'exact') {
                                    // utilizzo il data feed
                                    webix_field.suggest = {
                                        dynamic: true,
                                        // autofocus: true,
                                        body: {
                                            data: [],
                                            dataFeed: query.suggestUrl.replace('field', rule.filter.id) + '?limit=' + query.limit_suggest,

                                        }
                                    };
                                }
                                container.webix_text(webix_field);
                            }
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        }
                    }
                });
            }

            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                    $$(view_id).resize();
                }
            }
        });

        this.queryBuilder.on('afterUpdateRuleFilter.queryBuilder', function (e, rule, previousFilter) {
            // console.log('afterUpdateRuleFilter')
            // console.log(previousFilter)
            var container = rule.$el.find(".rule-filter-container");
            var genericId = rule.id.substring(0, rule.id.lastIndexOf("_") + 1);
            var elements = container.find("div[view_id^='filter_" + genericId + "']");
            var selectInput = container.find("select[name^='" + genericId + "']");
            var lastElement = $$(elements.last().attr("view_id"));
            var obj = rule.__;
            var next_number = 1;
            var extra = $$(this).extra_rules;

            var value_webix = $$("filter_" + rule.id).getValue();
            var value_jqb = container.find("select[name='" + rule.id + "_filter']").val();
            var cambiato = false;
            if(value_webix != value_jqb && value_jqb !== undefined){
                $$("filter_" + rule.id).setValue(value_jqb);
                cambiato = true;
            }

            if (obj.filter.follow && !cambiato) {
                var model = obj.filter.follow_model.split(".")
                var url = this.queryBuilder.filtersUrl.replace("app_label", model[0]).replace("model_name", model[1])
                var query = this.queryBuilder;
                var input_for_mod = selectInput[selectInput.length -1]

                if (selectInput.length > 1) {
                    var parts = selectInput[selectInput.length - 2].name.split('__')
                    if (parts.length == 2) {
                        next_number = parseInt(parts[1]) + 1
                    }
                }
                webix.ajax().get(url).then(function (data) {
                    var json = data.json();
                    var availableTypes = ["string", "integer", "double", "date", "time", "datetime", "boolean"]
                    var fields = [];
                    json['fields'].forEach(function (b, index, array) {
                        var type = b['type'];
                        if (availableTypes.indexOf(type) < 0)
                            type = "string";
                        var field = {id: b['id'], label: b['label'], type: type, operators: b['operators'], follow: true, model: json['model']};

                        field['follow'] = ('follow' in b) ? b['follow'] : false;
                        field['follow_model'] = ('follow_model' in b) ? b['follow_model'] : null;
                        if ('input' in b)
                            field['input'] = b['input']
                        if ('values' in b)
                            field['values'] = b['values']
                        if ('plugin' in b)
                            field['plugin'] = b['plugin']
                        if ('plugin_webix' in b)
                            field['plugin_webix'] = b['plugin_webix']
                        if ('plugin_config' in b)
                            field['plugin_config'] = b['plugin_config']
                        if ('value_separator' in b)
                            field['value_separator'] = b['value_separator']
                        if ('webix_type' in b)
                            field['webix_type'] = b['webix_type']
                        else
                            field['webix_type'] = 'string'
                        fields.push(field);
                    });

                    var operators = [];
                    json['operators'].forEach(function (a, index, array) {
                        var oper = {type: a.name, nb_inputs: a.nb_inputs, multiple: a.multiple, apply_to: ["string", "number", "datetime", "boolean"]}
                        if ('values' in a){
                            oper['values'] = a.values
                        }
                        operators.push(oper);
                    });

                    operators.forEach(function (b, index, array) {
                        var prensente = query.operators.find(function (el) {
                           return el.type == b.type
                        });
                        if(prensente === undefined){
                            query.operators.push(b);
                        }
                    });

                    //cambio i nomi delle due select
                    //devo cambiare in due parti l'id, con il medoto, per farlo riconosce a webix
                    //e al config che cosi ci posso accedere tranquillamente
                    $$("filter_" + rule.id).config.id = "filter_" + rule.id + "__" + next_number;
                    $$("filter_" + rule.id).id_setter("filter_" + rule.id + "__" + next_number);
                    // $$("filter_" + rule.id).define('id', "filter_" + rule.id + "__" + next_number);
                    $$("filter_" + rule.id).refresh();

                    if(webix.ui.views["filter_" + rule.id] != undefined){
                        delete webix.ui.views["filter_" + rule.id];
                    }

                    var old_name = input_for_mod.name
                    input_for_mod.name = old_name + "__" + next_number

                    // creo la nuova select per il jquerybuilder
                    var new_select = $('<select/>')
                            .attr('name', old_name)
                            .attr('class', 'form-control')
                            .css({float: "left"})
                            .append(
                                    $('<option/>').attr('value', -1).text('------')
                            )

                    // metto le opzioni appena scaricate, e le devo anche mettere dentro al querybuilder
                    fields.forEach(function (b, index, array) {
                       new_select.append(
                               $('<option/>').attr('value', b.id).text(b.label)
                       );
                       var prensente = query.filters.find(function (el) {
                           return el.id == b.id
                       });
                       if(prensente === undefined) {
                           query.filters.push(b)
                       }
                    });
                    $(container[0]).append(new_select)

                    // vado a creare la select di webix
                    var filterSelect = rule.$el.find("select[name='" + rule.id + "_filter']");
                    filterSelect.hide();

                    var options = [];
                    filterSelect.find("option").each(function() {
                        if ($(this).val() == "-1") {
                            options.push({id: $(this).val(), value: $(this).text(), $empty: true})
                            return;
                        }
                        options.push({id: $(this).val(), value: $(this).text()})
                    });

                    container.webix_combo({
                        id: "filter_" + rule.id,
                        options: options,
                        width: 200,
                        rule_id: rule.id,
                        css: {"float": "left"},
                        on: {
                            onChange: function (newv, oldv) {
                                var rule_id = this.config.rule_id;
                                var my_id = this.config.id;
                                var posfix = '';
                                var next = false;
                                var my_number = 0;
                                var comps = my_id.split('__')
                                if(comps.length > 1){
                                    my_number = parseInt(comps[1]);
                                    posfix = '__' + comps[1];
                                    next = true;
                                }
                                var selectors = rule.$el.find("select[name^='" + rule_id + "_filter']")
                                if (selectors.length > 1 && next == true) { //quasi di sicuro sono sempre entrambe vere
                                    for (var i = 0; i < selectors.length; i++) {
                                        var names = selectors[i].name.split('__')
                                        if (names.length > 1) {
                                            //significa che abbiamo preso uno che è nella forma __[n]
                                            //controllo se il suo __[n] è maggiore
                                            if (parseInt(names[1]) > my_number) {
                                                //delete dell'elemento
                                                rule.$el.find("select[name='" + selectors[i].name + "']").remove()
                                                $$("filter_" + rule_id + "__" + names[1]).destructor()
                                            }
                                        } else {
                                            //delete dell'elemento
                                            rule.$el.find("select[name='" + selectors[i].name + "']").remove()
                                            $$("filter_" + rule_id).destructor()
                                        }
                                    }
                                    //cambio il mio id e il name dell'oggetto jqb
                                    var old_id = this.config.id;
                                    this.id_setter('filter_' + rule_id); //webix component
                                    this.config.id = 'filter_' + rule_id; //webix component
                                    if (webix.ui.views[old_id] != undefined) {
                                        delete webix.ui.views[old_id];
                                    }
                                    var my_rule_select = rule.$el.find("select[name^='" + rule_id + "_filter" + posfix + "']");
                                    my_rule_select[0].name = my_rule_select[0].name.split('__')[0];
                                }
                                // da cambiare di nuovo tutti gli id superiori al mio .... come li prendo ?
                                // var selector = selectors[0]
                                // NB: non servirà più il posfix che tanto non ci sarà più
                                selectors = rule.$el.find("select[name='" + rule_id + "_filter']")
                                selectors.val(newv || "-1")
                                selectors.trigger("change");
                            }
                        }
                    });

                    $('[view_id=filter_' + rule.id + ']').css("z-index", "1100");

                    // controllo se devo andare in cascata...
                    // devo capire che regola sono che non lo so, [0, 1, 2, ....
                    // rule.id
                    var my_index = 0
                    var rules = query.$el.find("div[id*='_rule_']");
                    // trovo che indice sono, l'unico modo e un ciclo su tutti
                    for(var i=0; i < rules.length; i++){
                        if(rules[i].id === rule.id){
                            break;
                        }
                        my_index++;
                    }

                    if(my_index in extra){
                        // uso lo shift per una un pop della lista
                        var next_hop = extra[my_index]['hops'].shift();

                        if(next_hop === undefined){
                            delete extra[my_index];
                        }
                        else{
                            $$("filter_" + rule.id).setValue(next_hop);
                        }
                        $$("operator_" + rule.id).setValue(extra[my_index]['operator']);

                        var ruleInputs = rule.$el.find("input[name^='" + rule.id + "_value']");

                        var ruleInputsSelect = rule.$el.find("select[name^='" + rule.id + "_value']");

                        if(ruleInputs.length > 0 ){
                            if(ruleInputs.length > 1) {
                                for (var j = 0; j < ruleInputs.length; j++){
                                    $$('value_' + $(ruleInputs[j]).attr("name")).setValue(extra[my_index]['value'][j]);
                                }
                            }
                            else {
                                if(Array.isArray(extra[my_index]['value'])){
                                    $$('value_' + ruleInputs.attr('name')).setValue(extra[my_index]['value'].join(obj.filter.value_separator));
                                }else {
                                    $$('value_' + ruleInputs.attr('name')).setValue(extra[my_index]['value']);
                                }
                            }
                        }
                        if(ruleInputsSelect.length > 0 ){
                            $$('value_' + ruleInputsSelect.attr('name')).setValue(extra[my_index]['value']);
                        }
                        if(extra[my_index]['hops'].length === 0){
                            delete extra[my_index]
                        }
                    }


                });
            }
        });
        this.queryBuilder.on('afterUpdateRuleOperator.queryBuilder', function (e, rule, previousOperator) {
            // console.log('afterUpdateRuleOperator');
            // console.log(previousOperator);
            var operatorSelect = rule.$el.find("select[name='" + rule.id + "_operator']");
            var operator_selected = operatorSelect.val();
            var webix_operator = $$("operator_" + rule.id);
            var query = this.queryBuilder;

            if(operator_selected !== undefined && operator_selected !== null && operator_selected !== webix_operator){
                webix_operator.setValue(operator_selected);
            }

            var ruleInputs = rule.$el.find("input[name^='" + rule.id + "_value']");
            var container_input = rule.$el.find(".rule-value-container");
            if(ruleInputs.length > 0){
                ruleInputs.each(function () {
                    var ruleInput = $(this);
                    ruleInput.val('');
                    var type = rule.filter.webix_type;
                    var webix_input = $$('value_' + ruleInput.attr("name"));
                    webix_input.destructor();
                    var webix_input_geo_pick = $$('value_' + ruleInput.attr("name") + '_geo_pick');
                    if(webix_input_geo_pick != undefined){
                        webix_input_geo_pick.destructor();
                    }
                    var operator = rule.operator.type;
                    if(rule.operator.values != undefined){
                        var options_ = [];
                        for([key, value] of Object.entries(rule.operator.values)){
                            options_.push({id: key, value: value})
                        }
                        ruleInput.val('');
                        container_input.webix_select({
                            id: 'value_' + ruleInput.attr("name"),
                            view: 'combo',
                            options: options_,
                            width: 300,
                            on: {
                                onChange: function (newv, oldv) {
                                    ruleInput.val(newv);
                                    ruleInput.trigger("change");
                                }
                            }
                        });
                        $$('value_' + ruleInput.attr("name")).callEvent('onchange');
                        $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                    }
                    else{
                        if (type === 'date' && operator != 'year' && operator != 'month' && operator != 'day'
                                && operator != 'week_day' && operator != 'week' && operator != 'hour'
                                && operator != 'minute' && operator != 'second') {
                            //custom logic for __year __month .... spero
                            // 'year', 'month', 'day', 'week_day', 'week'
                            container_input.webix_datepicker({
                                id: 'value_' + ruleInput.attr("name"),
                                width: 300,
                                format: webix.Date.dateToStr("%Y-%m-%d"),
                                on: {
                                    onChange: function (newv, oldv) {
                                        var format_giorno_js = webix.Date.dateToStr("%Y-%m-%d");
                                        ruleInput.val(format_giorno_js(newv));
                                        ruleInput.trigger("change");
                                    }
                                }
                            });
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        }
                        else if (type === 'time' && operator != 'hour' && operator != 'minute' && operator != 'second') {
                            // 'hour', 'minute', 'second'
                            container_input.webix_datepicker({
                                id: 'value_' + ruleInput.attr("name"),
                                width: 300,
                                type: "time",
                                format: webix.Date.dateToStr("%H:%i:%s"),
                                on: {
                                    onChange: function (newv, oldv) {
                                        var format_ora_js = webix.Date.dateToStr("%H:%i:%s")
                                        ruleInput.val(format_ora_js(newv));
                                        ruleInput.trigger("change");
                                    }
                                }
                            });
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        }
                        else{
                            var webix_field = {
                                id: 'value_' + ruleInput.attr("name"),
                                width: 300,
                                on: {
                                    onChange: function (newv, oldv) {
                                        var val = newv;
                                        if(this.config.regex != undefined) {
                                            if (!this.config.regex.test(newv)) {
                                                if (oldv == null || oldv == undefined) {
                                                    oldv = 0
                                                }
                                                val = oldv;
                                                this.setValue(oldv);
                                            }
                                        }

                                        if (Array.isArray(val)) {
                                            ruleInput.val(val.join(rule.filter.value_separator));
                                        } else {
                                            ruleInput.val(val);
                                        }
                                        ruleInput.trigger("change");
                                        $$('querybuilder-container').resize();

                                        if(this.config.view == 'multicombo'){
                                            var values_set = this.getValue();
                                            var suggestion = [];
                                            values_set.split(rule.filter.value_separator).forEach(function (a, index, array) {
                                                suggestion.push({'id': a, 'value':a});
                                            })
                                            this.getList().parse(suggestion);
                                        }
                                    },
                                    onFocus: function(current_view, prev_view){
                                        if(this.config.suggest != undefined && this.config.suggest != null) {
                                            var suggest = $$(this.config.suggest);
                                            var l = suggest.getList();
                                            if(l.config.dataFeed != undefined && l.config.dataFeed != null) {
                                                suggest.show(this.getInputNode());
                                                l.load(l.config.dataFeed);
                                            }
                                        }
                                    }
                                }
                            }

                            if (type == 'integer') {
                                if (operator_selected === 'in') {
                                    // webix_field.regex = new RegExp('\^((-{0,1}\\d*)' + rule.filter.value_separator + '{0,1})*\$');
                                } else {
                                    webix_field.regex = new RegExp('\^-{0,1}\\d*\$');
                                }
                            }

                            if (type == 'double') {
                                if (operator_selected === 'in') {
                                    // webix_field.regex = new RegExp('\^((\\d+\(\\.\\d+\)\?)' + rule.filter.value_separator + '{0,1})*\$');
                                } else {
                                    webix_field.regex = new RegExp('\^\\d+\(\\.\\d+\)\?\$');
                                }
                            }
                            var rule_values = null;
                            if(rule.filter.values != undefined && rule.filter.values.length > 0) {
                                rule_values = [];
                                rule.filter.values.forEach(function (l, i) {
                                    for (var k in l) {
                                        rule_values.push({id: k, value: l[k]})
                                    }
                                })
                            }
                            if(rule.operator.multiple === true){
                                var suggest_multi;
                                if(rule.filter.values != undefined && rule.filter.values.length > 0){
                                    var options_multi = [];
                                    rule.filter.values.forEach(function (l, i) {
                                        for (var k in l) {
                                            options_multi.push({id: k, value: l[k]})
                                        }
                                    })
                                    suggest_multi = options_multi;
                                } else {
                                    suggest_multi = {
                                        dynamic: true,
                                        body: {
                                            data: [],
                                            dataFeed: query.suggestUrl.replace('field', rule.filter.id) + '?limit=' + query.limit_suggest
                                        }
                                    };
                                }
                                webix_field.suggest = suggest_multi;
                                webix_field.separator = ";";
                                container_input.webix_multicombo(webix_field);
                            } else if(rule.operator.pick_geometry === true){
                                webix_field.disabled = query.webgis_enable;
                                webix_field.width = 300;
                                if (query.webgis_enable) {
                                    var layers = $$('map').getLayersFromModel(rule.filter.model);
                                    var options_geo = [];
                                    layers.forEach(function (l, i) {
                                        if($$('map').overlayLayers[l.id].filters.spatial.length > 0){
                                            options_geo.push(l);
                                        }
                                    });
                                    var label_combo = 'Scegliere un layer WebGIS filtrato:';
                                    if (options_geo.length == 0) {
                                        label_combo = 'Nessn layer filtrato nel WebGIS';
                                    }
                                    container_input.webix_combo({
                                        id: 'value_' + ruleInput.attr("name") + '_geo_pick',
                                        view: 'combo',
                                        options: options_geo,
                                        width: 300,
                                        value: null,
                                        label: label_combo,
                                        labelPosition: 'top',
                                        on: {
                                            onChange: function (newv, oldv) {
                                                if (newv != null && newv !== '') {
                                                    var filter = $$('map').overlayLayers[newv].filters.spatial[0];
                                                    var id_input = this.config.id.replace('_geo_pick', '');
                                                    $$(id_input).setValue(filter);
                                                }
                                            }
                                        }
                                    });
                                }
                                container_input.webix_text(webix_field);
                            } else if(rule_values != null){
                                webix_field.options = rule_values;
                                container_input.webix_combo(webix_field);
                            } else {
                                if (rule.operator.type == 'exact') {
                                    // utilizzo il data feed
                                    webix_field.suggest = {
                                        dynamic: true,
                                        body: {
                                            data: [],
                                            dataFeed: query.suggestUrl.replace('field', rule.filter.id) + '?limit=' + query.limit_suggest
                                        }
                                    };
                                }
                                container_input.webix_text(webix_field);
                            }
                            $('[view_id=value_' + ruleInput.attr("name") + ']').css("z-index", "1100");
                        }


                        var old_value = ruleInput.val();
                        ruleInput.val('');
                        webix_input = $$('value_' + ruleInput.attr("name"));
                        webix_input.setValue(old_value);

                        // da inserire

                        if (type != 'date' && type != 'time') {
                            if (rule.operator.type == 'in') {
                                webix_input.refresh();
                            } else {
                                webix_input.define({placeholder: ''});
                                webix_input.refresh();
                            }
                        }
                    }
                });
            }
        });
        this.queryBuilder.on('afterUpdateRuleValue.queryBuilder', function (e, rule, prev){
            // console.log('afterUpdateRuleValue');
            var container = rule.$el.find(".rule-value-container");
            var ruleInputs = rule.$el.find("input[name^='" + rule.id + "_value']");
            var ruleInputsSelect = rule.$el.find("select[name^='" + rule.id + "_value']");
            if(ruleInputsSelect.length > 0){
                var value_webix = $$('value_' + ruleInputsSelect.attr('name')).getValue();
                var value_jqb = ruleInputsSelect.val();
                if(value_jqb !== undefined && value_jqb !== value_webix) {
                    $$('value_' + ruleInputsSelect.attr('name')).setValue(value_jqb);
                }
            }
            if(ruleInputs.length > 0) {
                ruleInputs.each(function () {
                    var value_jqb = $(this).val();
                    var value_webix = $$('value_' + $(this).attr('name')).getValue();
                    if(value_jqb !== undefined && value_jqb !== value_webix) {
                        $$('value_' + $(this).attr('name')).setValue(value_jqb);
                    }
                });
            }
        });
        this.queryBuilder.on('afterUpdateGroupCondition.queryBuilder', function (e, group, previusCondition) {
           // console.log("afterUpdateGroupCondition");
           var group_con = group.condition;
           var webix_group_condition = $$("cond_" + group.id);
           if(webix_group_condition !== undefined) {
               var webix_con = $$("cond_" + group.id).getValue();
               if (group_con !== webix_con && group_con !== undefined) {
                   $$("cond_" + group.id).setValue(group_con);
               }
           }
        });
        this.queryBuilder.on('afterUpdateGroupNot.queryBuilder', function (e, group){
            // console.log('afterUpdateGroupNot');
            var not_condition = group.not
            var webix_not = $$("not_" + group.id);
            if(webix_not.getValue() === 1 && not_condition === false){
                webix_not.setValue(not_condition);
            }
            if(webix_not.getValue() === 0 && not_condition === true){
                webix_not.setValue(not_condition);
            }
        });

        this.queryBuilder.on('getRules.queryBuilder.filter', function (e, level) {
            var tree = e.value
            var rules = this.queryBuilder.$el.find("div[id*='_rule_']");
            tree_visit(tree.rules, rules, 0, this.queryBuilder.filters)
            return tree;
        });

        this.queryBuilder.on('afterDeleteGroup.queryBuilder', function (e, rule) {
            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                    $$(view_id).resize();
                }
            }
        });
        this.queryBuilder.on('afterDeleteRule.queryBuilder', function (e, rule) {
            var view_id = this.parentNode.getAttribute('view_id');
            if(view_id !== '' && view_id !== undefined && view_id !== null){
                var view_id_parent = $(this.parentNode).parent()[0].getAttribute('view_id');
                if(view_id_parent !== '' && view_id_parent !== undefined && view_id_parent !== null) {
                    $$(view_id_parent).resize();
                    $$(view_id).resize();
                }
            }
        });
    },
    operators_setter: function (value) {
        if (!webix.isArray(value))
            value = [value];
        return value;
    },
    filters_setter: function (value) {
        if (!webix.isArray(value))
            value = [value];
        return value;
    },
    rules_setter: function (value) {
        if (!webix.isArray(value))
            value = [value];
        return value;
    },
    set_rules: function (query) {
        if(query !== undefined && query !== null) {
            if ('fks' in query && 'rules' in query) {
                this.extra_rules = query.fks;
                this.queryBuilder.setRules(query.rules);
            }
        }
    },
    get_rules: function () {
        return this.queryBuilder.getRules();
    }
}, webix.ui.template, webix.EventSystem);


function tree_visit(tree, rules, index, filters) {
    for(var i=0; i < tree.length; i++){
        var oggetto = tree[i]
        if('id' in oggetto) {
            var filtro = filters.find(function (el) {
                return el.id == oggetto.id
            });
            var rule_selections = $(rules[index]).find("select[name*='" + rules[index].id + "_filter']")
            var id_composed = '';
            if(rule_selections.length > 1){
                //significa che ho più di una selection cioè dei passaggi con FK
                //devo prendere i nomi e metterli in concatenazione
                rule_selections.each(function () {
                    var name_split = $(this).val().split('.')
                    if(id_composed === '') {
                        id_composed = id_composed + name_split[name_split.length - 1];
                    }else{
                        id_composed = id_composed + '__' + name_split[name_split.length - 1];
                    }
                })
            }
            else{
                var name_split = oggetto.id.split('.');
                id_composed = name_split[name_split.length - 1];
            }
            oggetto.id = id_composed;
            oggetto.field = id_composed;
            oggetto.input = filtro.input;
            index = index + 1;
        }
        else{
            index = tree_visit(oggetto.rules, rules, index, filters);
        }
    }
    return index;
}
