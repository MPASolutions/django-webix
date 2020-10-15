{% load django_webix_utils static i18n %}

function {{ view_prefix }}get_filters_qsets() {
    return []
}

function _{{ view_prefix }}action_execute(action, ids, all, response_type, short_description, modal_title, modal_ok, modal_cancel, input_params) {
    /*
    action (required) = action_key to be executed
    ids (required) = list of selected elements ids
    all (required) = boolean if all elements are selected
    response_type (required) = ['script', 'json', 'blank']
    short_description (not required)
    modal_title (required) = text to show in modal choices execution
    modal_ok (not required)
    modal_cancel (not required)
    params (not required) = paramters to post in action method
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
                        'params': JSON.stringify(input_params || {}),
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

{% if is_enable_actions %}

var {{ view_prefix }}actions_list = [
    {% for layer in layers %}
        {id: 'gotowebgis_{{ layer.layername }}', value: "{{_("Go to map")|escapejs}} ({{layer.layername}})"},
    {% endfor %}
    {% for action_key,action in actions.items %}
    {id: '{{ action_key }}', value: '{{action.short_description}}'}{% if not forloop.last %}, {% endif %}
    {% endfor %}
];

function {{ view_prefix }}actions_execute(action, ids, all) {
    {% for layer in layers %}
    if (action=='gotowebgis_{{ layer.layername }}') {
        $$("map").goToWebgisPks('{{layer.layername}}', '{{ pk_field_name }}', ids);
    }
    {% endfor %}
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
