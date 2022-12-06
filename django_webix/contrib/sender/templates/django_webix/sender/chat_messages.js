{% load static i18n humanize send_methods_utils %}

{% user_can_send as can_send %}

{% block content %}
    webix.ui([], $$('messages'));

    webix.html.addStyle("div[view_id=messages_list] div.webix_list_item { border: 0; }");

    $$("messages").addView({
        rows: [
            {
                view: "toolbar",
                rows: [
                    {
                        cols: [
                            {},
                            {view: "label", label: "{{ recipient.representation }}", align: "center"},
                            {}
                        ]
                    },
                    {
                        view: "search",
                        placeholder: "{{ _("Search..") }}",
                        on: {
                            onKeyPress: function (code, e) {
                                var $this = this;
                                setTimeout(function () {
                                    $$("messages_list").filter(function (obj) {
                                        return obj.body.toString().toLowerCase().indexOf($this.getValue().toLowerCase()) != -1;
                                    });
                                }, 10);
                            }
                        }
                    }
                ]
            },
            {
                view: "list",
                id: "messages_list",
                borderless: true,
                css: {"border": "none"},
                template: function (item) {
                    var sender = "";
                    if (item.sender !== "") {
                        sender = "<div style='display: inline-block; float: " + item.position + "'>" + item.sender + "</div><br/>";
                    }
                    return sender +
                        "<div style='max-width: 300px; margin: 5px 0; display: inline-block; float: " + item.position + "; border-radius: 15px; padding: 5px 10px; color: " + item.color + "; background-color: " + item.backgroundcolor + "'>" +
                        item.body + "<br/>" +
                        "<span style='font-size: x-small; float: right'>" + item.creation_date + "</span>" +
                        "</div>";
                },
                type: {
                    height: "auto"
                },
                on: {
                    onAfterRender: webix.once(function () {
                        {% with messages|last as last %}
                            setTimeout(function () {
                              $$("messages_list").showItem({{ last.id }});
                            }, 10);
                        {% endwith %}
                    })
                },
                data: [
                    {% for message in messages %}
                        {
                            id: "{{ message.id }}",
                            sender: "{{ message.sender|default_if_none:'' }}",
                            body: "{{ message.body|escapejs }}",
                            status: "{{ message.status }}",
                            creation_date: "{{ message.creation_date|naturaltime }}",
                            user: "{{ message.user }}",
                            position: "{{ message.position }}",
                            backgroundcolor: "{{ message.backgroundcolor }}",
                            color: "{{ message.color }}"
                        },
                    {% endfor %}
                ]
            },
            {% if can_send %}
                {
                    cols: [
                        {
                            view: 'textarea',
                            id: "response_message_body",
                            placeholder: '{{ _("Type your message") }}'
                        },
                        {
                            view: 'button',
                            value: "{{ _("Send") }}",
                            width: 100,
                            on: {
                                onItemClick: function (id, e) {
                                    var recipients = {};
                                    recipients["{{ contenttype }}"] = [];
                                    recipients["{{ contenttype }}"].push({{ recipient.pk }});

                                    var data = new FormData();

                                    data.append('send_methods', "{{ send_method }}");
                                    {% if typology_model.enabled %}
                                        data.append('typology', {{ typology.pk }});
                                    {% endif %}
                                    data.append('body', $$('response_message_body').getValue());
                                    data.append('recipients', JSON.stringify(recipients));

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
                                            $$('{{ webix_container_id }}').hideOverlay();
                                            load_js("{% url 'dwsender.messages_chat' section='messages' %}?contenttype={{ contenttype }}&recipient={{ recipient.pk }}&send_method={{ send_method }}");
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
                        }
                    ]
                }
            {% endif %}
        ]
    });
{% endblock %}
