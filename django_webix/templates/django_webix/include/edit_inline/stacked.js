$$('{{ inline.prefix }}-group').addView({
    rows: [
        {
            id: '{{ inline.prefix }}-form',
            rows: [
                {{ inline.management_form.as_webix|safe }},
                {% for field in inline %}
                    {
                        id: '{{ field.prefix|safe }}-inline',
                        rows: [{{ field.as_webix|safe }}]
                    },
                {% endfor %}
                {
                    css: 'empty-form',
                    id: '{{ inline.prefix }}-empty_form',
                    rows: [{{ inline.empty_form.as_webix|safe }}]
                }
            ]
        },
        {
            id: "{{ inline.prefix }}-add",
            view: "label",
            label: "<b style='cursor: pointer; color: #3498db;'>Aggiungi</b>",
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

                    // Add inline
                    $$('{{ inline.prefix }}-form').addView({
                        id: '{{ inline.prefix }}-' + parseInt(totalForms.getValue()) + '-inline',
                        rows: []
                    }, -1);
                    replace_prefix(empty_form.getChildViews(), totalForms, '{{ inline.prefix }}-' + parseInt(totalForms.getValue()) + '-inline');

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
                }
            }
        }
    ]
});

{# Delete trigger on all inlines #}
{% for row in inline %}
    delete_trigger("{{ row.prefix }}");
{% endfor %}

{# Rules event on all inlines #}
{% for row in inline %}
    {% for field in row %}
        add_rule("{{ field.auto_id }}");
    {% endfor %}
{% endfor %}
