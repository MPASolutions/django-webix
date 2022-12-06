{% load static i18n verbose_name field_type %}

{% block content %}
webix.ui([], $$('{{ webix_container_id }}'));

var custom_bool = function (obj, common, value) {
  if (value === true)
    return "<img style='width:12px;' src='{% static 'admin/img/icon-yes.svg' %}'>";
  else
    return "<img style='width:12px;' src='{% static 'admin/img/icon-no.svg' %}>";
};

function match(a, b) {
    return a.toString() == b;
}

$$("{{webix_container_id}}").addView({
    rows: [
        {
            view: "accordion",
            multi: true,
            cols: [
                {% for datatable in datatables %}
                {
                    header: "{{ datatable.verbose_name_plural }}",
                    collapsed: {{ datatable.collapsed|yesno:"true,false" }},
                    body: {
                        gravity: 1,
                        rows: [
                            {% if use_dynamic_filters and datatable.filters|length > 0 %}
                            {
                                cols: [
                                    {
                                        id: 'filter_switch_{{ datatable.model }}',
                                        view: "switch",
                                        value: 0,
                                        labelAlign: 'right',
                                        labelWidth: 40,
                                        label: "{{ _("AND")|escapejs }}",
                                        labelRight: "{{ _("OR")|escapejs }}",
                                        width: 120,
                                        on: {
                                            onChange: function (newv, oldv) {
                                                var dt = $$("{{ datatable.model }}");
                                                dt.clearAll();

                                                // Values
                                                var switchValue = newv === 0 ? 'and' : 'or';
                                                var filterValue = $$('filter_{{ datatable.model }}').getValue();

                                                // Filtering
                                                if (filterValue !== '') {
                                                    var pks = filterValue.split(",");
                                                    for (var i = 0; i < pks.length; i++) {
                                                        pks[i] = "filter_pk=" + pks[i];
                                                    }
                                                    pks = pks.join("&");

                                                    var url = '{% url 'dwsender.getlist' %}?';
                                                    url += 'contentype={{ datatable.model }}&';
                                                    url += pks + '&';
                                                    url += 'and_or_filter=' + switchValue;

                                                    dt.load(url);
                                                }
                                            }
                                        }
                                    },
                                    {
                                        id: 'filter_{{ datatable.model }}',
                                        view: "multicombo",
                                        placeholder: "{{_("Filter the list by applying filters")|escapejs}}",
                                        labelWidth: 0,
                                        options: [
                                            {% for filter in datatable.filters %}
                                            {
                                                'id': "{{ filter.id }}",
                                                'value': "{{ filter.value|safe|escapejs }}"
                                            },
                                            {% endfor %}
                                        ],
                                        on: {
                                            onChange: function (newv, oldv) {
                                                var dt = $$("{{ datatable.model }}");
                                                dt.clearAll();

                                                // Values
                                                var switchValue = $$('filter_switch_{{ datatable.model }}').getValue() === 0 ? 'and' : 'or';
                                                var filterValue = newv.filter(function (el) {
                                                  return el != '';
                                                });

                                                // Filtering
                                                if (filterValue.length > 0) {
                                                    var pks = [];
                                                    for (var i = 0; i < filterValue.length; i++) {
                                                        pks[i] = "filter_pk=" + filterValue[i];
                                                    }
                                                    pks = pks.join("&");

                                                    var url = '{% url 'dwsender.getlist' %}?';
                                                    url += 'contentype={{ datatable.model }}&';
                                                    url += pks + '&';
                                                    url += 'and_or_filter=' + switchValue;

                                                    dt.load(url);
                                                }
                                            }
                                        }
                                    }
                                ]
                            },
                            {view: "spacer", height: 10},
                            {% endif %}
                            {
                                id: '{{ datatable.model }}',
                                view: "datatable",
                                multiselect: true,
                                navigation: true,
                                select: "row",
                                scheme: {
                                    $init: function (obj) {
                                        obj.index = this.count();
                                    }
                                },
                                columns: [
                                    {
                                        id: "index",
                                        header: "",
                                        width: 40,
                                        minWidth: 40
                                    },
                                    {
                                        id: "checkbox_action",
                                        header: {content: "masterCheckbox", css: "center"},
                                        template: "{common.checkbox()}",
                                        width: 40,
                                        minWidth: 40,
                                        maxWidth: 40
                                    },
                                    {% for field in datatable.fields %}
                                    {
                                        id: "{{ field }}",
                                        header: ["{% get_verbose_field_name datatable.model field %}",
                                            {% field_type datatable.model field as field_t %}
                                            {% if field_t == "BooleanField" %}
                                                {
                                                    content: 'selectFilter',
                                                    options: [
                                                        {id: '', value: '{{ _("All")|escapejs }}'},
                                                        {id: 'true', value: '{{ _("Yes")|escapejs }}'},
                                                        {id: 'false', value: '{{ _("No")|escapejs }}'}
                                                    ],
                                                    compare: match
                                                },
                                            {% else %}
                                                {content: "textFilter"}
                                            {% endif %}
                                        ],
                                        {% if field_t == "BooleanField" %}
                                            template: custom_bool,
                                        {% endif %}
                                        adjust: "all"
                                    },
                                    {% endfor %}
                                ],
                                data: [],
                                on: {
                                    onBeforeLoad: function () {
                                        $$('{{ webix_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                    },
                                    onAfterLoad: function () {
                                        $$('{{ webix_container_id }}').hideOverlay();
                                    },
                                    onCheck: function (rowId, colId, state) {
                                        if (state) {
                                            this.select(rowId, true);
                                        } else {
                                            this.unselect(rowId, true);
                                        }
                                    },
                                    "data->onStoreUpdated": function () {
                                        this.data.each(function (obj, i) {
                                            if (obj !== undefined) {
                                                obj.index = i + 1;
                                            }
                                        })
                                    }
                                }
                            }
                        ]
                    }
                },
                {view: "spacer", width: 10},
                {% endfor %}
            ]
        },
        {
            view: "toolbar",
            margin: 5,
            cols: [
                {
                    view: "richselect",
                    id: "action_combo",
                    maxWidth: "300",
                    value: 1,
                    label: '{{ _("Action")|escapejs }}',
                    options: [
                        {id: 1, value: "------------"},
                        {% if send_methods|length > 0 %}
                            {id: "send", value: "{{ _("Send")|escapejs }}"},
                        {% endif %}
                    ]
                },
                {
                    view: "button",
                    id: "action_button",
                    value: "{{ _("Go")|escapejs }}",
                    inputWidth: 50,
                    width: 50,
                    on: {
                        onItemClick: function () {
                            var action = $$("action_combo").getValue();

                            var recipients = {};
                            {% for datatable in datatables %}
                                $$("{{ datatable.model }}").getSelectedItem(true).forEach(function (element) {
                                    if (recipients["{{ datatable.model }}"] === undefined) {
                                        recipients["{{ datatable.model }}"] = [];
                                    }
                                    recipients["{{ datatable.model }}"].push(element['id']);
                                })
                            {% endfor %}

                            {% if send_methods|length > 0 %}
                                if (action === "send") {
                                    django_webix_sender.open(recipients);
                                }
                            {% endif %}
                        }
                    }
                },
                {
                    view: "label",
                    id: "count_bottom_label_selected",
                    label: "0 {{ _("selected of")|escapejs }}",
                    hidden: true,
                    width: 150,
                    paddingX: 0,
                    align: "right"
                },
                {
                    view: "label",
                    id: "count_bottom_label_total",
                    label: "0",
                    hidden: true,
                    width: 40,
                    paddingX: 0,
                    align: "left"
                }
            ]
        }
    ]
});

/**
 * Funzione per contare il numero di elementi nelle varie datatables
 *
 * @returns {number} numero di elementi nelle datatables
 */
var getDatatablesItems = function () {
    var total = 0;
    var selected = 0;
    {% for datatable in datatables %}
        total += $$('{{ datatable.model }}').count();
        selected += $$('{{ datatable.model }}').getSelectedItem(true).length;
    {% endfor %}

    $$("count_bottom_label_selected").setValue(selected + " {{_("selected of")|escapejs}}");
    $$("count_bottom_label_total").setValue(total);
    $$("count_bottom_label_selected").show();
    $$("count_bottom_label_total").show();

    return total;
}

{# Attach events to datatables and loads data if `filters` is not installed #}
{% for datatable in datatables %}
    $$("{{ datatable.model }}").on_click.webix_cell = function () {
        return false;
    };
    $$("{{ datatable.model }}").$view.oncontextmenu = function () {
        return false;
    };

    $$('{{ datatable.model }}').attachEvent("onAfterLoad", getDatatablesItems);
    $$('{{ datatable.model }}').attachEvent("onAfterFilter", getDatatablesItems);
    $$('{{ datatable.model }}').attachEvent("onAfterDelete", getDatatablesItems);
    $$('{{ datatable.model }}').attachEvent("onAfterSelect", getDatatablesItems);
    $$('{{ datatable.model }}').attachEvent("onAfterUnSelect", getDatatablesItems);
    {% if not use_dynamic_filters or datatable.filters|length == 0 %}
        var dt = $$("{{ datatable.model }}");
        dt.load("{% url 'dwsender.getlist' %}?contentype={{ datatable.model }}");
    {% endif %}
{% endfor %}

// Include window class
var django_webix_sender = undefined;
$.ajax({
    url: "{% url 'dwsender.sender_window' %}",
    dataType: "script",
    success: function () {
        django_webix_sender = new DjangoWebixSender();
    },
    error: function () {
        webix.message({
            type: "error",
            expire: 10000,
            text: '{{ _("Unable to load sender class")|escapejs }}'
        });
    }
});

{% endblock %}
