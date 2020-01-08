{% load django_webix_utils %}
{# Errors #}
{% block webix_form_errors %}
    {% if form.errors %}
        webix.message({type: "error", expire: 10000, text: "{{ form.errors|safe|escapejs }}"});
    {% endif %}
{% endblock %}

{% block webix_inline_errors %}
    {% for inline in inlines %}
        {% for field in inline %}
            {% if field.errors %}
                webix.message({type: "error", expire: 10000, text: "{{ field.errors|safe|escapejs }}"});
            {% endif %}
        {% endfor %}
    {% endfor %}
{% endblock %}


{# Form #}
{% block webix_form %}
    $$("{{ webix_container_id }}").addView({
        borderless: true,
        view: 'form',
        elements: [
            {% if inlines|length > 0 %}
                {
                    view: "tabbar",
                    id: '{{ form.webix_id }}-inlines-tabbar',
                    value: "{{ form.webix_id }}-group",
                    //optionWidth: 150,
                    multiview: true,
                    options: [
                        {
                            id: '{{ form.webix_id }}-group',
                            value: "{{ form.get_name }}"
                        },
                        {% for inline in inlines %}
                            {% if not inline.get_container_id %}
                                {
                                    id: '{{ inline.get_default_container_id }}',
                                    value: "<div style='position: relative'>{{ inline.get_name }} <span class='webix_badge' style='background-color:#888 !important; margin-top: -2px; margin-right: 5px;'><strong>" + {{ inline.initial_form_count }} + "</strong></span></div>"
                                },
                            {% endif %}
                        {% endfor %}
                    ]
                },
            {% endif %}
            {
                animate: false,
                id: '{{ form.webix_id }}-inlines',
                cells: [
                    {% block webix_form_elements %}
                        {
                            id: '{{ form.webix_id }}-group',
                            rows: [
                                {{ form.as_webix|safe }}
                            ]
                        },
                    {% endblock %}
                    {% for inline in inlines %}
                        {% if not inline.get_container_id %}
                            {
                                id: '{{ inline.get_default_container_id }}',
                                rows: []
                            },
                        {% endif %}
                    {% endfor %}
                ]
            }
        ],
        on: {
            onAfterValidation: function (result, value) {
                if (!result) {
                    var text = "";
                    for (var key in value) {
                        text += "<li>" + key + "</li>"
                    }
                    webix.message({
                        type: "error",
                        text: "Devi compilare tutti i campi richiesti prima di poter salvare questo form!<br><br>Errore nei seguenti campi:<br>" + text
                    });
                }
            }
        },
        rules: {
            {% block webix_form_rules %}
                {# Table rules #}
                {% for field_name, rules in form.get_rules.items %}
                    '{{ field_name }}': function (value) {
                        return {% for r in rules %}{{r.rule}}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} && {% endif %}{% endfor %}
                    },
                {% endfor %}
            {% endblock %}

            {% block webix_inline_rules %}
                {# Inlines rules #}
                {% for inline in inlines %}
                    {% for field_name, rules in inline.get_rules.items %}
                        '{{ field_name }}': function (value) {
                            return {% for r in rules %}{{r.rule}}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} && {% endif %}{% endfor %}
                        },
                    {% endfor %}
                {% endfor %}
            {% endblock %}
        },
        id: '{{ form.webix_id }}',
        name: '{{ form.webix_id }}',
        scroll: 'y'
    });

    {% block webix_inline_prefix_rules %}
        var _prefix_rules = {};
        {% for inline in inlines %}
            {% for field_name, rules in inline.get_rules_template.items %}
                _prefix_rules['{{ field_name }}'] = function (value) {
                    return {% for r in rules %}{{ r.rule }}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} && {% endif %}{% endfor %}
                };
            {% endfor %}
        {% endfor %}
    {% endblock %}


    {% block webix_include_inlines %}
        {% for inline in inlines %}
            {% if inline.template_name %}
                {% include inline.template_name %}
            {% else %}
                {% include "django_webix/include/edit_inline/stacked.js" %}
            {% endif %}
        {% endfor %}
    {% endblock %}

{% endblock %}


{% block webix_inline_functions %}
    {% include "django_webix/include/form_utils.js" %}
{% endblock %}
