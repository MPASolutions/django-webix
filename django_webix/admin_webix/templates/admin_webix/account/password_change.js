{% load static i18n %}

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
            template: '<div style="width:100%; text-align:center;"><strong>{{ _("Cambio password utente")|escapejs }} {{ user }}</strong></div>'
        }
    ]
}, 0);

$$("{{ webix_container_id }}").addView({
    cols:[
        {},
        {
            rows: [
                {
                    height: 30,
                },
                {% block extra_pre_form %}
                {% endblock %}
                {
                    id: "password_change_form",
                    view: "form",
                    type: "form",
                    scroll: false,
                    width: 400,
                    elements: [
                        {
                            labelWidth: 130,
                            view: "text",
                            id: "id_old_password",
                            name: "old_password",
                            type: "password",
                            label: "{{ _("Password attuale")|escapejs }}",
                            required: true
                        },
                        {
                            labelWidth: 130,
                            view: "text",
                            name: "new_password1",
                            id: "id_new_password1",
                            type: "password",
                            label: "{{ _("Nuova password")|escapejs }}",
                            required: true
                        },
                        {
                            labelWidth: 130,
                            view: "text",
                            name: "new_password2",
                            id: "id_new_password2",
                            type: "password",
                            label: "{{ _("Conferma password")|escapejs }}",
                            required: true
                        },
                        {
                            margin: 5,
                            cols: [
                                {
                                    view: "button",
                                    id: 'id_button_change_password',
                                    label: "{{ _("Conferma")|escapejs }}",
                                    click: function () {
                                        if ($$('password_change_form').validate()) {
                                            $$('{{ webix_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                            console.log($$('password_change_form').getValues());
                                            $.ajax({
                                                url: "{% url 'admin_webix:password_change' %}",
                                                dataType: "script",
                                                type: "POST",
                                                data: $$('password_change_form').getValues(),
                                                success: function (data, textStatus, jqXHR) {
                                                    $$('{{ webix_container_id }}').hideOverlay();
                                                },
                                                error: function (jqXHR, textStatus, errorThrown) {
                                                }
                                            });
                                            //webix.send("{% url 'admin_webix:password_change' %}", $$('password_change_form').getValues());
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {}
    ]
});

$$('password_change_form').setValues({csrfmiddlewaretoken: "{{ csrf_token }}"});

{% block webix_form_errors %}
    {% if form.errors %}
        webix.message({type: "error", expire: 10000, text: "{{ form.errors|safe|escapejs }}"});
    {% endif %}
{% endblock %}
