{% load django_webix_utils static i18n %}

var errors = [];
{% if is_errors_on_popup %}
    {% include "django_webix/include/form_errors_popup.js" %}
{% else %}
    {% include "django_webix/include/form_errors_message.js" %}
{% endif %}

function _{{ view_prefix }}datatable_count() {
    if ($$('{{ view_prefix }}select_all_checkbox').getValue() == 0) {
        view_count_selected = 0;
        $$("{{ view_prefix }}datatable").eachRow(function (id) {
            if ((this.getItem(id) != undefined) && (this.getItem(id).checkbox_action)) {
                view_count_selected += 1;
            }
        });
        return view_count_selected;
    } else {
        return $$('{{ view_prefix }}datatable').view_count_total;
    }
}

function _{{ view_prefix }}action_execute(action, ids, all, response_type, short_description, modal_title, modal_ok, modal_cancel, input_params, callback_success, callback_error, reload_list) {
    /*
    action (required) = action_key to be executed
    ids (required) = list of selected elements ids
    all (required) = boolean if all elements are selected
    response_type (required) = ['script', 'json', 'blank']
    short_description (not required)
    modal_title (required) = text to show in modal choices execution
    modal_ok (not required)
    modal_cancel (not required)
    params (not required) = parameters to post in action method
    */
    webix.confirm({
        title: short_description,
        ok: modal_ok,
        cancel: modal_cancel,
        text: modal_title + "</br><b>" + _{{ view_prefix }}datatable_count() + " {{_("elements")|escapejs}}</b> {{_("selected")|escapejs}}",
        callback: function (confirm) {
            if (confirm == true) {
                $$('{{ view_prefix }}datatable').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                if ((response_type == 'json') || (response_type == 'script')) {
                    var _params = $.extend({}, webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']);
                    _params['action'] = action;
                    _params['params'] = JSON.stringify(input_params || {});
                    _params['csrfmiddlewaretoken'] = getCookie('csrftoken');
                    if (all == false) {
                        _params['ids'] = ids.join(',');
                    }

                    $.ajax({
                        url: "{{ url_list|safe }}",
                        type: "POST",
                        dataType: response_type,
                        data: _params,
                        error: function (jqXHR, textStatus, errorThrown) {
                            // if 400 then is form invalid
                            if (jqXHR.status == 400) {
                                var responseJson = jQuery.parseJSON(jqXHR.responseText);
                                show_errors(responseJson.errors);
                            } else {
                                {% if is_errors_on_popup %}
                                    webix.alert({
                                        title: "{{ _("Oops! Something went wrong...")|escapejs }}",
                                        text: "{{ _("Action is not executable")|escapejs }}",
                                        type:"alert-error"
                                    });
                                {% else %}
                                    webix.message({
                                        text: "{{ _("Action is not executable")|escapejs }}",
                                        type: "error",
                                        expire: 10000
                                    });
                                {% endif %}
                            }
                            if (callback_error) {
                                callback_error();
                            }
                            $$('{{ view_prefix }}datatable').hideOverlay();
                        },
                        success: function (data) { // TODO gestire response
                            if (response_type === 'json') {
                                var title = "";
                                var message = "";
                                var message_on_popup = data.message_on_popup || false;
                                var message_type = data.message_type;

                                if ((message_type==undefined)&&(data.status!=undefined)){
                                    if (data.status === false) {
                                        message_type = 'alert-error';
                                    }
                                }

                                if (data.status === true) title = "{{_("Action successful")|escapejs}}";
                                else title = "{{_("Oops! Something went wrong...")|escapejs}}"

                                if (data.message !== undefined) message = data.message;

                                if (message_on_popup) {
                                    webix.alert({
                                        title: title,
                                        text: message,
                                        type: message_type
                                    });
                                } else {
                                    webix.message({
                                        text: message || title,
                                        type: message_type || "info",
                                        expire: 10000
                                    });
                                }

                                if (data.status === true) {
                                    if (data.redirect_url != null) {
                                        load_js(data.redirect_url, undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending = true);
                                    }
                                    if (callback_success) {
                                        callback_success();
                                    }
                                    if (reload_list) {
                                        try {
                                            {{ view_prefix }}apply_filters();
                                        } catch (error) { // only for custom purpose
                                            $$('{{ view_prefix }}datatable').filterByAll();
                                        }
                                    }
                                    // callback success by js
                                    try {
                                        window['{{ view_prefix }}' + action + '_callback_success']();
                                    } catch (error) { // only for custom purpose
                                    }
                                } else {
                                    if (callback_error) {
                                        callback_error();
                                    }
                                }
                            }
                            $$('{{ view_prefix }}datatable').hideOverlay();
                        }
                    });
                } else if (response_type == 'blank') {
                    var form = document.createElement("form");
                    form.setAttribute("method", "post");
                    form.setAttribute("action", "{{ url_list|safe }}");
                    form.setAttribute("target", "view");

                    var _fields = [
                        ['action', action],
                        ['params', JSON.stringify(input_params || {})],
                        ['csrfmiddlewaretoken', getCookie('csrftoken')],
                    ];

                    var _params = $.extend({}, webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']);
                    for (var key in _params) {
                        if (_params.hasOwnProperty(key)) {
                            _fields.push([key, _params[key] || ""]);
                        }
                    }

                    if (all == false) {
                        _fields.push(['ids', ids.join(',')])
                    }
                    // add standard fields
                    $.each(_fields, function (index, value) {
                        var hiddenField = document.createElement("input");
                        hiddenField.setAttribute("type", "hidden");
                        hiddenField.setAttribute("name", value[0]);
                        hiddenField.setAttribute("value", value[1]);
                        form.appendChild(hiddenField);
                    });
                    // add form fields
                    for (var key in input_params) {
                        var hiddenField = document.createElement("input");
                        hiddenField.setAttribute("type", "hidden");
                        hiddenField.setAttribute("name", key);
                        hiddenField.setAttribute("value", input_params[key]);
                        form.appendChild(hiddenField);
                    }
                    document.body.appendChild(form);
                    form.target = '_blabk';
                    form.submit();
                    if (callback_success) {
                        callback_success();
                    }
                    $$('{{ view_prefix }}datatable').hideOverlay();
                } else {
                    $$('{{ view_prefix }}datatable').hideOverlay();
                }

            } else {
                if (callback_error) {
                    callback_error();
                }
            }
        }
    })
}
