{% load static i18n verbose_name field_type %}

{% block content %}
webix.ui([], $$('{{ webix_container_id }}'));

$$("{{ webix_container_id }}").addView({
    rows: [
        {
            view: "toolbar",
            elements: [
                {
                    id: 'send_method',
                    view: 'combo',
                    value: "{{ request.GET.send_method }}",
                    label: "{{_("Send method")|escapejs}}",
                    labelWidth: 130,
                    width: 400,
                    labelAlign: 'right',
                    options: [
                        {id: "", value: "", $empty: true},
                        {% for send_method in send_methods %}
                            {
                                id: "{{ send_method.key|safe|escapejs }}",
                                value: "{{ send_method.value|safe|escapejs }}"
                            },
                        {% endfor %}
                    ],
                    on: {
                        onChange: function (newv, oldv) {
                            var url = "{% url 'dwsender.invoices' %}";
                            url += (url.indexOf('?') >= 0 ? '&' : '?') + $.param({'send_method': newv});
                            load_js(url);
                        }
                    }
                }
            ]
        },
        {
            view: "scrollview",
            scroll: "y",
            body: {
                rows: [
                    {% for sender in senders %}
                    {
                        autoheight: true,
                        rows: [
                            {
                                view: "template",
                                template: "{{ sender.name|safe|escapejs }} - {{ sender.send_method|safe|escapejs }}",
                                type: "header"
                            },
                            {
                                id: 'datatable_{{ forloop.counter0 }}',
                                view: "datatable",
                                autoheight: true,
                                select: false,
                                navigation: false,
                                footer: true,
                                columns: [
                                    {
                                        id: "period",
                                        header: "{{_("Period")|escapejs}}",
                                        footer: "<b>{{_("TOTAL")|escapejs}}</b>",
                                        fillspace: true
                                    },
                                    {
                                        id: "messages_success",
                                        header: "{{_("Success")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "messages_unknown",
                                        header: "{{_("Unknowm status")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "messages_fail",
                                        header: "{{_("Not send")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "messages_invoiced",
                                        header: "{{_("Invoiced")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "messages_to_be_invoiced",
                                        header: "{{_("To be invoiced")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "price_invoiced",
                                        header: "{{_("Price invoiced")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "price_to_be_invoiced",
                                        header: "{{_("Price to be invoiced")|escapejs}}",
                                        footer: {content: "summColumn"},
                                        fillspace: true
                                    },
                                    {
                                        id: "rating",
                                        header: "",
                                        template: function () {
                                            return '<div class="webix_view webix_control webix_el_button webix_secondary"><div class="webix_el_box"><button type="button" class="webix_button">{{_("marks as billed")|escapejs}}</button></div></div>';
                                        },
                                        width: 200
                                    }
                                ],
                                data: [
                                    {% for period in sender.periods %}
                                    {
                                        'period': "{{ period.period|safe|escapejs }}",
                                        'messages_success': {{ period.messages_success|default:0|safe|escapejs }},
                                        'messages_unknown': {{ period.messages_unknown|default:0|safe|escapejs }},
                                        'messages_fail': "{{ period.messages_fail|default:0|safe|escapejs }}",
                                        'messages_invoiced': "{{ period.messages_invoiced|default:0|safe|escapejs }}",
                                        'messages_to_be_invoiced': "{{ period.messages_to_be_invoiced|default:0|safe|escapejs }}",
                                        'price_invoiced': "{{ period.price_invoiced|default:0|safe|escapejs }}",
                                        'price_to_be_invoiced': "{{ period.price_to_be_invoiced|default:0|safe|escapejs }}",
                                        'send_method_code': "{{ sender.send_method_code|safe|escapejs }}",
                                        'sender': "{{ sender.name|safe|escapejs }}"
                                    },
                                    {% endfor %}
                                ],
                                onClick: {
                                    webix_button: function (ev, id) {
                                        marks_invoiced(this, id);
                                    }
                                }
                            }
                        ],
                        paddingY: 10
                    },
                    {% endfor %}
                ]
            }
        }
    ]
});

{% for sender in senders %}
  //$$('datatable_{{ forloop.counter0 }}').adjustRowHeight();
{% endfor %}

var marks_invoiced = function (datatable, id) {
    var period = datatable.getItem(id.row).period;
    var messages_unknown = datatable.getItem(id.row).messages_unknown;
    var send_method = datatable.getItem(id.row).send_method_code;
    var sender = datatable.getItem(id.row).sender;
    var masks_billed = function (period) {
        webix.confirm({
            title: "{{_("Confirmation")|escapejs}}",
            text: "{{_("Are you sure you want to mark these communications as billed?")|escapejs}}",
            ok: "{{_("Yes")|escapejs}}",
            cancel: "{{_("No")|escapejs}}",
            callback: function (result) {
                var data = {
                    'period': period,
                    'sender': sender,
                    'send_method': send_method
                }
                {% if request.GET.year %}
                    data['year'] = "{{ request.GET.year }}";
                {% endif %}
                if (result) {
                    // TODO: segnare come fatturati
                    webix.ajax().post("{% url 'dwsender.invoices' %}", data, {
                        error: function (text, data, XmlHttpRequest) {
                            alert("error");
                        },
                        success: function (text, data, XmlHttpRequest) {
                            var url = "{% url 'dwsender.invoices' %}";
                            var send_method = $$('send_method').getValue();
                            var params = {};
                            if (send_method !== '') {
                                params['send_method'] = send_method;
                            }
                            url += (url.indexOf('?') >= 0 ? '&' : '?') + $.param(params);
                            load_js(url);
                        }
                    });
                }
            }
        });
    }

    if (messages_unknown > 0) {
        webix.alert({
            title: "{{_("Caution!")|escapejs}}",
            text: "{{_("There are unknown status for this communication")|escapejs}}",
            callback: function () {
                masks_billed(period);
            }
        });
    } else {
        masks_billed(period);
    }
}

{% endblock %}
