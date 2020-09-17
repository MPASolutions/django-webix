{% load django_webix_utils static i18n %}

if (form_validate('{{ form.webix_id }}')) {
    if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').showOverlay !== undefined)
        $$('{{ webix_overlay_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
    else if ($$('{{ webix_container_id }}') !== undefined && $$('{{ webix_container_id }}') !== null && $$('{{ webix_container_id }}').showOverlay !== undefined)
        $$('{{ webix_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");

    var form_data = new FormData();
    var form_data_webix_elements = [];

    {% block pre_form_data %}{% endblock %}

    form_data_webix_elements.push($$('{{ form.webix_id }}'));
    $.each(form_data_webix_elements, function (index, value) {
        $.each(value.elements, function (i, el) {
            var elementAttributes = typeof el.config !== "undefined" ? el.config : el.data;

            if (elementAttributes.view != 'uploader') {
                form_data.append(elementAttributes.name, el.getValue());
            }
            else {
                // console.log('id_' + elementAttributes.name + '_clean')
                // if ($$('id_' + elementAttributes.name + '_clean').getValue() == 1) {
                //     // devo eliminarlo
                //     console.log('elimino il file provo')
                //     form_data.append(elementAttributes.name, '');
                // } else {
                //     el.files.data.each(function (obj) {
                //         if (obj !== undefined) {
                //             form_data.append(elementAttributes.name, obj.file, obj.file.name);
                //         }
                //     });
                // }
                el.files.data.each(function (obj) {
                    if (obj !== undefined) {
                        form_data.append(elementAttributes.name, obj.file, obj.file.name);
                    }
                });
            }
        });
    });

    {% block post_form_data %}{% endblock %}

    $.ajax({
        {% if not object.pk and url_create and url_create != '' %}
            url: "{{ url_create }}{% if extra_params_button %}{% if not '?' in url_create %}?{% else %}&{% endif %}{{ extra_params_button }}{% endif %}",
        {% elif url_update and url_update != '' %}
            url: "{{ url_update }}{% if extra_params_button %}{% if not '?' in url_create %}?{% else %}&{% endif %}{{ extra_params_button }}{% endif %}",
        {% endif %}
        dataType: "script",
        type: "POST",
        data: form_data,
        processData: false,
        contentType: false,
        success: function (data, textStatus, jqXHR) {
            {% block save_success %}{% endblock %}
            webix.ui.resize();
            if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                $$('{{ webix_overlay_container_id }}').hideOverlay();
            else if ($$('{{ webix_container_id }}') !== undefined && $$('{{ webix_container_id }}') !== null && $$('{{ webix_container_id }}').hideOverlay !== undefined)
                $$('{{ webix_container_id }}').hideOverlay();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            {% block save_error %}{% endblock %}
        }
    });
}
