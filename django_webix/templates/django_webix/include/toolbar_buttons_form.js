{% load django_webix_utils static %}

/**
 * Returns if a form is valid
 *
 * @returns {boolean}
 */
function form_validate() {
    var form_data_webix_elements = [];
    form_data_webix_elements.push($$('{{ form.webix_id }}'));

    var status = true;

    $.each(form_data_webix_elements, function (index, value) {
        var valid = value.validate({hidden: true, disabled: true});
        if (valid == false) {
            status = false;
        }
    });

    return status;
}


$$("{{ view.webix_view_id|default:"content_right" }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    cols: [
        {% if has_delete_permission and form.instance.get_url_delete and form.instance.get_url_delete != '' %}
            {
                view: "button",
                type: "danger",
                align: "left",
                icon: "eraser",
                id: 'delete',
                label: "Elimina",
                width: 120,
                click: function () {
                    load_js("{% url form.instance.get_url_delete object.pk %}");
                }
            },
        {% endif %}
        {% block extra_buttons_left %}{% endblock %}
        {$template: "Spacer"},
        {% block extra_buttons_right %}{% endblock %}
        {% if not object.pk and has_add_permission or object.pk and has_change_permission %}
            {
                view: "button",
                type: "form",
                align: "right",
                icon: "save",
                id: 'save',
                label: "Salva i dati",
                width: 120,
                click: function () {
                    if (form_validate()) {
                        $$('content_right').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");

                        var form_data = new FormData();
                        var form_data_webix_elements = [];

                        form_data_webix_elements.push($$('{{ form.webix_id }}'));
                        $.each(form_data_webix_elements, function (index, value) {
                            $.each(value.elements, function (i, el) {
                                if (el.data.view != 'uploader') {
                                    form_data.append(el.data.name, el.getValue())
                                } else {
                                    if (el.files.getFirstId()) {
                                        var id = el.files.getFirstId();
                                        form_data.append(el.data.name, el.files.getItem(id).file, el.files.getItem(id).file.name);
                                    }
                                }
                            });
                        });

                        $.ajax({
                            url: "{% if not object.pk and form.instance.get_url_create and form.instance.get_url_create != '' %}{% url form.instance.get_url_create %}{% elif object.get_url_update and object.get_url_update != '' %}{% url object.get_url_update object.pk %}{% endif %}",
                            dataType: "script",
                            type: "POST",
                            data: form_data,
                            processData: false,
                            contentType: false,
                            success: function () {
                                webix.ui.resize();
                                $$('content_right').hideOverlay();
                            }
                        });
                    }
                }
            }
        {% endif %}
    ]
});


{# Check toolbar elements number #}
if ($$('main_toolbar_form').getChildViews().length < 2) {
    $$("{{ view.webix_view_id|default:"content_right" }}").removeView($$('main_toolbar_form'));
}
