{% extends 'django_webix/include/edit_inline/tabular.js' %}

{% block webix_content %}

function replace_view(id_selector, config) {
    var field = $$(id_selector);
    var field_parent = field.getParentView();
    config['id'] = id_selector;
    config['name'] = field.config.name+'';
    config['value'] = field.getValue();
    var here = field_parent.index(id_selector);
    field_parent.removeView(id_selector);
    field_parent.addView(config, here);
    field_parent.resize();
}

function set_widget_model_field_value(selector){
    var model_field_id = $$('id_' + selector + '-model_field').getValue();
    $$('id_' + selector + '-value').disable();
    if (model_field_id!=''){
        $.ajax({
            url: "{% url 'dwextra_fields.modelfield.config' 0 %}".replace('0', model_field_id),
            dataType: "json",
            type: "GET",
            data: {},
            success: function (msg) {
                if (msg.options.length > 0) {
                    var config = {view: 'combo', options:msg.options}
                } else {
                    if (msg.widget == 'IntegerField') {
                        var config = {view: 'text'};
                    } else if (msg.widget == 'FloatField') {
                        var config = {view: 'text'};
                    } else if (msg.widget == 'CharField') {
                        var config = {view: 'text'};
                    } else if (msg.widget == 'DateField') {
                        var config = {
                            view: 'datepicker',
                            format: "%d/%m/%Y",
                            stringResult: true,
                            editable: true
                        };
                    } else if (msg.widget == 'BooleanField') {
                        var config = {view: 'checkbox'};
                    }
                }
                replace_view('id_' + selector + '-value', config);
                $$('id_' + selector + '-value').enable();
            },
            error: function () {
            }
        });
    }
}

function trigger_modelfieldvalue_set(selector){
    $$('id_' + selector + '-model_field').attachEvent("onChange", function (newv, oldv) {
        set_widget_model_field_value(selector)
    });
    set_widget_model_field_value(selector);
}
{{block.super}}
{% endblock %}
