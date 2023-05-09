{% load static %}

{% block webix_content %}
webix.ui({
    view: "window",
    id: "{{ webix_container_id }}",
    width: 550,
    maxHeigth: 600,
    scrool: 'y',
    position: "center",
    modal: true,
    move: true,
    resize: true,
    head: {
        view: "toolbar", cols: [
            {view: "label", label: '{{modal_header|escapejs}}'},
            {
                view: "button",
                label: '{{_("Close")|escapejs}}',
                width: 100,
                align: 'right',
                click: "$$('{{ webix_container_id }}').destructor();"
            }
        ]
    },
    body: {
        view: 'form',
        id: '{{ form.webix_id }}',
        name: '{{ form.webix_id }}',
        borderless: true,
        elements: [
            {{ form.as_webix|safe }},
            {
                id: '{{ action_key }}_toolbar_form',
                view: "toolbar",
                margin: 5,
                cols: [
                    {$template: "Spacer"},
                    {
                        id: '{{ form.webix_id }}_set',
                        view: "tootipButton",
                        type: "form",
                        align: "right",
                        label: "{{modal_click|escapejs}}",
                        click: function () {
                            if ($$('{{ form.webix_id }}').validate({hidden: true, disabled: true})) {
                                webix.extend($$('{{ form.webix_id }}'), webix.OverlayBox);
                                $$('{{ form.webix_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                _{{ parent_view.get_view_prefix }}action_execute(
                                    '{{ action_key }}',
                                    '{{ ids|default_if_none:'' }}'.split(','),
                                    {{ all }},
                                    '{{ response_type }}',
                                    '{{ short_description }}',
                                    '{{ modal_title }}',
                                    '{{ modal_ok }}',
                                    '{{ modal_cancel }}',
                                    $$('{{ form.webix_id }}').getValues(),
                                    function () {
                                        $$('{{ form.webix_id }}').hideOverlay();
                                        $$('{{ webix_container_id }}').destructor()
                                    },
                                    function () {
                                        $$('{{ form.webix_id }}').hideOverlay();
                                    },
                                    {% if reload_list %}true{% else %}false{% endif %}
                                )
                            }
                        }
                    },
                    {$template: "Spacer"}
                ]
            }
        ],
        rules: {
            {% for field_name, rules in form.get_rules.items %}
            '{{ field_name }}': function (value) {
                return {% for r in rules %}{{r.rule}}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} &&
                {% endif %}{% endfor %}
            },
            {% endfor %}
        },
    }
}).show();

{% block extrajs_post %}{% endblock %}

{% endblock %}
