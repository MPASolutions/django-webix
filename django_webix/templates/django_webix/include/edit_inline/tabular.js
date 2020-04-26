{% load django_webix_utils i18n %}

$$('{{ inline.get_container_id|default_if_none:inline.get_default_container_id }}').addView({
    rows: [
        {% if inline|length > 0 %}
        {{ inline.0.get_tabular_header|safe }},
        {% endif %}
        {
            id: '{{ inline.prefix }}-form',
            borderless: true,
            type: 'clean',
            rows: [
                {{ inline.management_form.as_webix|safe }},
                {% for inline_form in inline %}
                {
                    id: '{{ inline_form.prefix|safe }}-inline',
                    borderless: true,
                    type: 'clean',
                    body: {
                        borderless: true,
                        type: 'clean',
                        id: '{{ inline_form.prefix|safe }}-inline-body',
                        cols: [{{ inline_form.as_webix|safe }}]
                    }
                },
                {% endfor %}
                {
                    //css: 'empty-form',
                    hidden: true,
                    id: '{{ inline.prefix|safe }}-empty_form',
                    borderless: true,
                    type: 'clean',
                    body: {
                        borderless: true,
                        type: 'clean',
                        id: '{{ inline.prefix|safe }}-empty_form-body',
                        cols: [{{ inline.empty_form.as_webix|safe }}]
                    }
                }
            ]
        },
        {% if inline.has_add_permission %}
        {
            cols: [
                {
                    id: "{{ inline.prefix }}-add",
                    view: "tootipButton",
                    type: "form",
                    align: "right",
                    label: '{{_("Add")|escapejs}}',
                    width: 150,
                    on: {
                        onBeforeRender: function () {
                            var totalForms = $$("id_{{ inline.prefix }}-TOTAL_FORMS");
                            var maxNumForms = $$("id_{{ inline.prefix }}-MAX_NUM_FORMS");

                            var showAddButton = maxNumForms.getValue() === '' || (maxNumForms.getValue() - totalForms.getValue()) > 0;

                            // TODO: non funziona nel caso in cui non ci siano inlines (0 inlines). Non entra proprio in questo evento

                            if (showAddButton) {
                                this.show();
                            } else {
                                this.hide();
                            }
                        },
                        onItemClick: function () {
                            // Default form
                            var empty_form = $$("{{ inline.prefix }}-empty_form");

                            // Management form
                            var totalForms = $$("id_{{ inline.prefix }}-TOTAL_FORMS");
                            var maxNumForms = $$("id_{{ inline.prefix }}-MAX_NUM_FORMS");

                            // create new accordion item
                            create_inline(empty_form, parseInt(totalForms.getValue()), '{{ inline.prefix }}-form');

                            // Add delete button event
                            var inline_id = '{{ inline.prefix }}-' + parseInt(totalForms.getValue());
                            delete_trigger(inline_id);

                            // Increment management form values
                            totalForms.setValue(parseInt(totalForms.getValue()) + 1);

                            // Check if user can add another inline
                            var showAddButton = maxNumForms.getValue() === '' || (maxNumForms.getValue() - totalForms.getValue()) > 0;
                            if (showAddButton) {
                                this.show();
                            } else {
                                this.hide();
                            }

                            {% block extra_trigger %}
                            if (typeof trigger_{{inline.prefix}} === "function") {
                                trigger_{{inline.prefix}}(inline_id);
                            }
                            {% endblock %}

                        }
                    }
                },
                {}
            ]
        }
        {% endif %}
    ]
});

{# Delete trigger on all inlines #}
{% for row in inline %}
delete_trigger("{{ row.prefix }}");
{% block extra_trigger_init %}
if (typeof trigger_{{inline.prefix}} === "function") {
    trigger_{{inline.prefix}}("{{ row.prefix }}");
}
{% endblock %}
{% endfor %}

{# Rules event on all inlines #}
{% for row in inline %}
{% for field in row %}
add_rule("{{ field.auto_id }}");
{% endfor %}
{% endfor %}
