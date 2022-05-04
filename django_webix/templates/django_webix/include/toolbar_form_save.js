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
                el.files.data.each(function (obj) {
                    if (obj !== undefined) {
                        form_data.append(elementAttributes.name, obj.file, obj.file.name);
                    }
                });
            }
        });
    });

    {% block post_form_data %}{% endblock %}
    if ($$('{{ form.webix_id }}-inlines-tabbar')!=undefined) {
        var active_tab = $$('{{ form.webix_id }}-inlines-tabbar').getValue() + '';
    }
    $.ajax({
        {% if not object.pk and url_create and url_create != '' %}
            url: "{{ url_create|safe }}{% if extra_params_button %}{% if not '?' in url_create %}?{% else %}&{% endif %}{{ extra_params_button }}{% endif %}",
        {% elif url_update and url_update != '' %}
            url: "{{ url_update|safe }}{% if extra_params_button %}{% if not '?' in url_update %}?{% else %}&{% endif %}{{ extra_params_button }}{% endif %}",
        {% elif url_send and url_send != '' %}
            url: "{{ url_send|safe }}{% if extra_params_button %}{% if not '?' in url_send %}?{% else %}&{% endif %}{{ extra_params_button }}{% endif %}",
        {% endif %}
        dataType: {% block datatype %}"script"{% endblock %},
        type: "POST",
        data: form_data,
        processData: false,
        contentType: false,
        success: function (data, textStatus, jqXHR) {
            {% block save_success %}{% endblock %}
            webix.ui.resize();
            {% if '_continue=true' in extra_params_button %}
            if ($$('{{ form.webix_id }}-inlines-tabbar')!=undefined) {
                $$('{{ form.webix_id }}-inlines-tabbar').setValue(active_tab);
            }
            {% endif %}
            if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                $$('{{ webix_overlay_container_id }}').hideOverlay();
            else if ($$('{{ webix_container_id }}') !== undefined && $$('{{ webix_container_id }}') !== null && $$('{{ webix_container_id }}').hideOverlay !== undefined)
                $$('{{ webix_container_id }}').hideOverlay();
            if (typeof {{ form.webix_id|comma_to_underscore }}_success === "function"){
                {{ form.webix_id|comma_to_underscore }}_success();
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            {% block save_error %}{% endblock %}
        }
    });
}
