{% load django_webix_utils i18n %}

{# Errors #}
{% include "django_webix/include/form_errors_server.js" %}
{% if is_errors_on_popup %}
    {% include "django_webix/include/form_errors_popup.js" %}
{% else %}
    {% include "django_webix/include/form_errors_message.js" %}
{% endif %}

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
                        value: "{% if default_id_tabbar %}{{ default_id_tabbar }}{% else %}{{ inlines.0.get_container_id }}{% endif %}",
                        //optionWidth: 150,
                        multiview: true,
                        options: [
                            {% for inline in inlines %}
                                {% if inline.auto_position %}
                                    {
                                        id: '{{ inline.get_container_id }}',
                                        value: "<div style='position: relative'>{{ inline.get_name|escapejs }} <span class='webix_badge' style='background-color:#888 !important; margin-top: -2px; margin-right: 5px;'><strong>" + {{ inline.initial_form_count }} + "</strong></span></div>"
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
                                {% if inline.auto_position %}
                                    {
                                        id: '{{ inline.get_container_id }}',
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
                    errors = [];
                    for (var item in value) {
                        errors.push({
                            "label": $$('{{ form.webix_id }}').elements[item].config.label,
                            "error": "{{ _("Empty or incorrect value")|escapejs }}"
                        });
                    };
                    show_errors(errors);
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
