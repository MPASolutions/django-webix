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
            {% block webix_form_elements %}
                {{ form.as_webix|safe }},
                {% if inlines %}
                    {
                        view: "tabbar",
                        id: '{{ form.webix_id }}-inlines-tabbar',
                        value: "{{ inlines.0.get_default_container_id }}",
                        //optionWidth: 150,
                        multiview: true,
                        options: [
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
                    {
                        animate: false,
                        id: '{{ form.webix_id }}-inlines',
                        cells: [
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
                {% endif %}
            {% endblock %}
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
