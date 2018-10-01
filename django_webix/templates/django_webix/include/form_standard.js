webix.ui([], $$("{{ view.webix_view_id|default:"content_right" }}"));


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
    $$("{{ view.webix_view_id|default:"content_right" }}").addView({
        borderless: true,
        view: 'form',
        elements: [
            {% if inlines|length > 0 %}
            {
                view: "tabbar",
                id: '{{ form.webix_id }}-inlines-tabbar',
                value: "{{ form.webix_id }}-group",
                optionWidth: 150,
                multiview: true,
                options: [
                    {
                        "id": '{{ form.webix_id }}-group',
                        "value": "{{ form.get_name }}",
                    },
                    {% for inline in inlines %}
                    {
                        "id": '{{ inline.prefix }}-group',
                        "value": "{{ inline.get_name }}"
                    },
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
                            "id": '{{ form.webix_id }}-group',
                            rows: [
                                {{ form.as_webix|safe }},
                            ]
                        },
                    {% endblock %}
                    {% for inline in inlines %}
                    {
                        "id": '{{ inline.prefix }}-group',
                        rows: []
                    },
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
            {% if inline.0.style == 'tabular' %}
                {% include "django_webix/include/edit_inline/tabular.js" %}
            {% elif inline.0.style == 'stacked' %}
                {% include "django_webix/include/edit_inline/stacked.js" %}
            {% else %}
                {% include "django_webix/include/edit_inline/stacked.js" %}
            {% endif %}
        {% endfor %}
    {% endblock %}

{% endblock %}


{% block webix_inline_functions %}
    {% include "django_webix/include/form_utils.js" %}
{% endblock %}
