{% load static i18n %}

/**
 * Django Webix Sender window class
 *
 * @constructor
 */
function DjangoWebixSender() {
    /**
     * Window object
     *
     * @type {webix.ui.baseview | webix.ui}
     */
    var sender_window = undefined;

    var initialSendMethods = [
        {% for initial_send_method in initial_send_methods %}
            "{{ initial_send_method.method }}.{{ initial_send_method.function }}",
        {% endfor %}
    ];

    /**
     * Create window helper
     *
     * @param recipients
     * @param default_text
     */
    var check_recipients_count = function (recipients, default_text) {
        if (sender_window) {
            sender_window.destructor();
        }
        sender_window = create_window(recipients, default_text);
        sender_window.show();
    }

    /**
     * Returns form elements
     *
     * @param recipients
     * @param default_text
     * @returns {*[]}
     */
    var get_elements = function (recipients, default_text) {
        var elements = [];

        elements.push({
            view: "multicombo",
            id: 'django-webix-sender-form-send_methods',
            name: 'send_methods',
            label: "{{ _("Send methods")|escapejs }}",
            labelWidth: 140,
            labelAlign: 'right',
            value: initialSendMethods.toString(),
            options: [
                {% for send_method in send_methods %}
                    {
                        id: "{{ send_method.method }}.{{ send_method.function }}",
                        value: "{{ send_method.verbose_name }}"
                    },
                {% endfor %}
            ],
            on: {
                onChange(newVal, oldVal) {
                    //console.log(newVal)
                    set_rules(newVal);
                    {% if 'skebby' in send_method_types or 'email' in send_method_types or 'storage' in send_method_types or 'telegram' in send_method_types %}
                        if ($$("django-webix-sender-form-send_methods").getValue().split(',').filter(
                                function(e) {return e.startsWith('skebby.') || e.startsWith('email.') || e.startsWith('storage.') || e.startsWith('telegram.')}
                                ).length > 0){
                            $$("django-webix-sender-form-attachments").show();
                            $$("django-webix-sender-form-attachments_list").show();
                        } else {
                            $$("django-webix-sender-form-attachments").hide();
                            $$("django-webix-sender-form-attachments_list").hide();
                            $$("django-webix-sender-form-attachments").setValue();
                        }
                    {% endif %}
                    {% if 'email' in send_method_types or 'storage' in send_method_types %}
                        if ($$("django-webix-sender-form-send_methods").getValue().split(',').filter(function(e) {return e.startsWith('email.') || e.startsWith('storage.')}).length > 0) {
                            $$('django-webix-sender-form-subject').show();
                        } else {
                            $$('django-webix-sender-form-subject').hide();
                            $$('django-webix-sender-form-subject').setValue();
                        }
                    {% endif %}
                }
            }
        });
        elements.push({
            view: "template",
            template: "<hr />",
            type: "clean",
            height: 20
        });

        {% if typology_model.enabled %}
            elements.push({
                view: "combo",
                id: 'django-webix-sender-form-typology',
                name: 'typology',
                label: '{{ _("Typology")|escapejs }}',
                labelWidth: 140,
                labelAlign: 'right',
                suggest: {
                    view: "suggest",
                    keyPressTimeout: 400,
                    body: {
                        dataFeed: "{% url 'webix_autocomplete_lookup' %}?app_label=dwsender&model_name=messagetypology"
                    },
                    url: "{% url 'webix_autocomplete_lookup' %}?app_label=dwsender&model_name=messagetypology&filter[value]="
                }
            });
        {% endif %}
        {% if 'email' in send_method_types or 'storage' in send_method_types %}
            elements.push({
                view: 'text',
                id: 'django-webix-sender-form-subject',
                name: 'subject',
                label: '{{ _("Subject")|escapejs }}',
                labelWidth: 140,
                labelAlign: 'right',
                hidden: initialSendMethods.filter(function(e) {return e.startsWith('email.') || e.startsWith('storage.')}).length === 0
            });
        {% endif %}
        elements.push({
            view: "textarea",
            id: 'django-webix-sender-form-body',
            name: 'body',
            height: 150,
            value: default_text !== undefined ? default_text : '',
            on: {
                onKeyPress: function () {
                    webix.delay(function () {
                        var count = $$("django-webix-sender-form-body").getValue().length;
                        $$("django-webix-sender-form-length").setValue(count + " {{ _("characters")|escapejs }}");
                    });
                }
            }
        });
        elements.push({
            view: "label",
            id: "django-webix-sender-form-length",
            label: "0 {{ _("characters")|escapejs }}",
            align: "right"
        });
        {% if 'skebby' in send_method_types or 'email' in send_method_types or 'storage' in send_method_types or 'telegram' in send_method_types %}
            elements.push({
                view: "uploader",
                id: "django-webix-sender-form-attachments",
                value: "{{ _("Attach file")|escapejs }}",
                link: "django-webix-sender-form-attachments_list",
                autosend: false,
                hidden: initialSendMethods.filter(function(e) {return e.startsWith('skebby.') || e.startsWith('email.') || e.startsWith('storage.') || e.startsWith('telegram.')}).length === 0
            });
            elements.push({
                view: "list",
                id: "django-webix-sender-form-attachments_list",
                type: "uploader",
                autoheight: true,
                hidden: initialSendMethods.filter(function(e) {return e.startsWith('skebby.') || e.startsWith('email.') || e.startsWith('storage.') || e.startsWith('telegram.')}).length === 0
            });
        {% endif %}
        elements.push({
            view: 'button',
            label: '{{ _("Send")|escapejs }}',
            on: {
                onItemClick: function () {
                    if (!$$("django-webix-sender-form").validate({hidden: true})) {
                        webix.message({
                            type: "error",
                            expire: 10000,
                            text: '{{ _("You have to fill in all the required fields")|escapejs }}'
                        });
                        return;
                    }

                    var data = new FormData();
                    data.append('send_methods', $$('django-webix-sender-form-send_methods').getValue());
                    {% if typology_model.enabled %}
                        data.append('typology', $$('django-webix-sender-form-typology').getValue());
                    {% endif %}
                    {% if 'email' in send_method_types or 'storage' in send_method_types %}
                        data.append('subject', $$('django-webix-sender-form-subject').getValue());
                    {% endif %}
                    data.append('body', $$('django-webix-sender-form-body').getValue());
                    {% if 'skebby' in send_method_types or 'email' in send_method_types or 'storage' in send_method_types or 'telegram' in send_method_types %}
                        $$("django-webix-sender-form-attachments").files.data.each(function (obj) {
                            data.append('file_' + obj.id, obj.file);
                        });
                    {% endif %}
                    data.append('recipients', JSON.stringify(recipients));

                    $.ajax({
                        type: "POST",
                        enctype: 'multipart/form-data',
                        url: "{% url 'dwsender.send' %}",
                        data: data,
                        processData: false,
                        contentType: false,
                        cache: false,
                        timeout: 600000,
                        success: function (result) {
                            var text = "";
                            result.forEach(function (element) {
                                var send_method = element['send_method'].split(".", 1)[0];
                                var valids = "{{ _("Valid recipients: ")|escapejs }}" + element['result']['valids'];
                                var invalids = "{{ _("Invalids recipients: ")|escapejs }}" + element['result']['invalids'];
                                var duplicates = "{{ _("Duplicate recipients: ")|escapejs }}" + element['result']['duplicates'];
                                text += "<b>" + send_method + "</b>" + "<br />" + valids + "<br />" + invalids + "<br />" + duplicates + "<br /><br />";
                            });
                            text += "{{ _("Are you sure to send this message?")|escapejs }}";

                            webix.confirm({
                                title: "{{ _('Confirmation')|escapejs }}",
                                text: text,
                                ok: "{{ _("Yes")|escapejs }}",
                                cancel: "{{ _("No")|escapejs }}",
                                callback: function (result) {
                                    if (result) {
                                        $$('{{ webix_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                        data.append('presend', false);
                                        $.ajax({
                                            type: "POST",
                                            enctype: 'multipart/form-data',
                                            url: "{% url 'dwsender.send' %}",
                                            data: data,
                                            processData: false,
                                            contentType: false,
                                            cache: false,
                                            timeout: 600000,
                                            success: function (data) {
                                                // Generate message string
                                                var result = "";
                                                data.forEach(function (element) {
                                                    result += element["result"]["status"];
                                                    result += "</br>"
                                                });

                                                $$('{{ webix_container_id }}').hideOverlay();
                                                webix.alert({
                                                    title: "{{ _("Results")|escapejs }}",
                                                    text: result
                                                });
                                                sender_window.destructor();
                                            },
                                            error: function () {
                                                $$('{{ webix_container_id }}').hideOverlay();
                                                webix.message({
                                                    type: "error",
                                                    expire: 10000,
                                                    text: '{{ _("Unable to send messages")|escapejs }}'
                                                });
                                            }
                                        });
                                    }
                                }
                            });
                        },
                        error: function () {
                            $$('{{ webix_container_id }}').hideOverlay();
                            webix.message({
                                type: "error",
                                expire: 10000,
                                text: '{{ _("Unable to send messages")|escapejs }}'
                            });
                        }
                    });
                }
            }
        });

        return elements;
    }

    /**
     * Return form rules
     *
     * @param send_methods
     * @returns {*}
     */
    var get_rules = function (send_methods) {
        var rules = {
            "send_methods": webix.rules.isNotEmpty,
            {% if typology_model.enabled and typology_model.required %}
                "typology": webix.rules.isNotEmpty,
            {% endif %}
            "body": webix.rules.isNotEmpty
        };

        // Add subject not empty rule
        if (send_methods.filter(function(e) {return e.startsWith('email.') || e.startsWith('storage.')}).length > 0) {
            rules['subject'] = webix.rules.isNotEmpty;
        }

        return rules;
    }

    /**
     * Set form rules
     *
     * @param send_methods
     */
    var set_rules = function (send_methods) {
        $$("django-webix-sender-form").config.rules = get_rules(send_methods);
    }

    /**
     * Create webix window form
     *
     * @param recipients
     * @param default_text
     * @returns {webix.ui.baseview | webix.ui}
     */
    var create_window = function (recipients, default_text) {
        return new webix.ui({
            view: "window",
            id: "django-webix-sender",
            width: 800,
            height: 500,
            modal: true,
            move: true,
            resize: true,
            position: "center",
            head: {
                view: "toolbar", cols: [
                    {
                        view: "label",
                        label: '{{ _("Send")|escapejs }}'
                    },
                    {
                        view: "button",
                        label: '{{ _("Close")|escapejs }}',
                        width: 100,
                        align: 'right',
                        click: function () {
                          $$('django-webix-sender').destructor();
                        }
                    }
                ]
            },
            body: {
                rows: [{
                    view: 'form',
                    id: 'django-webix-sender-form',
                    padding: 10,
                    elements: get_elements(recipients, default_text),
                    rules: get_rules(initialSendMethods)  // Initial send methods
                }]
            },
            footer: {}
        });
    }

    /**
     * Open django webix sender window
     *
     * @param recipients
     * @param default_text
     */
    this.open = function (recipients, default_text) {
        var total = 0;
        Object.keys(recipients).forEach(function (key) {
            total += recipients[key].length;
        });

        if (total === 0) {
            webix.alert({
                title: "{{ _("Caution!")|escapejs }}",
                text: "{{ _("There are no recipients for this communication")|escapejs }}",
                callback: function () {
                    check_recipients_count(recipients, default_text);
                }
            });
        } else {
            check_recipients_count(recipients, default_text);
        }
    }
}
