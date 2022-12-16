webix.ui([], $$("{{ webix_container_id }}"));

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>{{ _("Password reset")|escapejs }}</strong></div>'
        }
    ]
}, 0);


$$("{{ webix_container_id }}").addView({
    cols: [
        {},
        {
            rows: [
                {$template: "Spacer", height: 20},
                {
                    view: "template",
                    template: '{{ _("Forgot password? Enter your email address below, and we will send you instructions to set up a new one")|escapejs }}',
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {$template: "Spacer", height: 20},
                {
                    view: "form",
                    id: "{{ form.webix_id }}",
                    minWidth: 500,
                    borderless: true,
                    elements: [
                        {{ form.as_webix|safe }},
                        {
                            margin: 5,
                            cols: [
                                {
                                    view: "button",
                                    id: 'id_button_reset_password',
                                    label: '"{{ _("Confirm")|escapejs }}',
                                    click: function () {
                                        if ($$('{{ form.webix_id }}').validate()) {
                                            webix.send("{% url 'dwadmin:password_reset' %}", $$('{{ form.webix_id }}').getValues());
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                },
            ]
        },
        {}
    ]
});


{% if form.errors %}
{% for field in form %}
  {% for error in field.errors %}

    $$('{{ form.webix_id }}').markInvalid("{{ field.name }}", "{{ error|safe }}");
    $$("id_{{ field.name }}").define('bottomPadding', Math.ceil("{{ error|safe }}".length / 50) * 18);
  {% endfor %}
{% endfor %}
{% for error in form.non_field_errors %}
  webix.message({
    type: "error",
    text: "{{ error|safe }}",
    expire: 10000
  });
{% endfor %}
{% endif %}


$$('{{ form.webix_id }}').setValues({csrfmiddlewaretoken: "{{ csrf_token }}"});
