function create_form_parameters(json_data) {
    _forms = [];
    _params = [];
    for(let i = 0; i < json_data.length; i++) {
        field_params = json_data[i]
        if(field_params['field_name'] === 'help') {
            $$('command_help').removeView('command_help_in');
            $$('command_help').addView({id:'command_help_in', cols:[
                {width:150},
                {view:'template', margin:0,borderless:true, template:'<p style="margin:0; font-size: 12px;">'+field_params['value']+'</p>'}
                ]})
        } else {
            conf = {
                id: field_params['field_name'],
                label: field_params['field_name'],
                labelWidth: 150,
                labelAlign: "right"
            }
            correctly_identified = true;
            switch (field_params['data_type']) {
                case 'string':
                    conf['view'] = "text"
                    if ("value" in field_params) {
                        conf['value'] = field_params['value']
                    }
                    break;
                case 'int':
                    conf['view'] = "counter"
                    conf['min'] = -100
                    if ("value" in field_params) {
                        conf['value'] = field_params['value']
                    } else {
                        conf['value'] = 0
                    }
                    break;
                case 'bool':
                    conf['view'] = "checkbox"
                    if ("value" in field_params) {
                        conf['value'] = field_params['value']
                    }
                    break;
                case 'choice':
                    conf['view'] = "combo"
                    conf['options'] = field_params['options']
                    if ("value" in field_params) {
                        conf['value'] = field_params['value']
                    }
                    break;
                case 'date':
                    conf['view'] = "datepicker"
                    if ("value" in field_params) {
                        conf['value'] = field_params['value']
                    }
                    break;
                default:
                    ok = false
                    break;
            }
            if (correctly_identified) {
                _forms.push(conf);
                _params.push(field_params['field_name'])
                if ("help" in field_params) {
                    _forms.push({cols:[//minheight: 20,autoheight:true
                        {width:150},
                        {
                            view:'template',
                            autoheight:true,
                            borderless:true,
                            template:'<p style="margin:0;font-size: 12px;">'+ field_params['help'].replaceAll('<', '[').replaceAll('>', ']') +'</p>'
                        }
                    ]});
                }
            }
        }
    }
    $$("form_parameters").removeView('form_parameters_in')
    $$("form_parameters").addView({id: 'form_parameters_in', rows:_forms}, 0)
    for (let i = 0; i < _params.length; i++) {
        $$(_params[i]).attachEvent("onChange", function (newv, oldv) {
            synk_parameters(_params[i], newv);
        });
    }
}

function synk_parameters(id_field, val){
    json_data = JSON.parse($$("id_parameters").getValue())
    for (let i = 0; i < json_data.length; i++) {
        if (json_data[i]['field_name'] == id_field){
            json_data[i]['value'] = val
        }
    }
    $$("id_parameters").setValue(JSON.stringify(json_data))
}

function load_parameters(){
    $.ajax(
        {
            'url': "{% url "dwcommands_manager.commandexecution.parameters" command_name='000' %}".replace('000', $$("id_command_name").getValue()),
            'method': 'GET',
            'success': function(msg){
                create_form_parameters(msg['parameters'])
                $$("id_parameters").setValue(JSON.stringify(msg['parameters']))
            },
        }
    );
}

if ($$("id_parameters").getValue() != ''){
    create_form_parameters(JSON.parse($$("id_parameters").getValue()))
}

$$("id_command_name").attachEvent("onChange", function (newv, oldv) {
    load_parameters();
});
