{% load django_webix_utils static %}

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    cols: [
        {% block button_delete %}
            {% if not remove_disabled_buttons %}
              {% if object.pk  and url_delete and url_delete != '' %}
                {
                    id: '{{ form.webix_id }}_delete',
                    view: "tootipButton",
                    type: "danger",
                    align: "left",
                    label: "Elimina",
                    {% if not has_delete_permission %}
                    disabled: true,
                    tooltip: "{% autoescape off %}{{ info_no_delete_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    width: 120,
                    click: function () {
                        load_js("{{ url_delete }}");
                    }
                },
              {% endif %}
            {% endif %}
        {% endblock %}
        {% block extra_buttons_left %}{% endblock %}
        {$template: "Spacer"},
        {% block extra_buttons_right %}{% endblock %}
        {% block button_save %}
            {% if not remove_disabled_buttons or remove_disabled_buttons and not object.pk and not has_add_permission or remove_disabled_buttons and object.pk and not has_change_permission %}
                {% if is_enable_button_save_continue %}
                {
                    id: '{{ form.webix_id }}_save_continue',
                    view: "tootipButton",
                    type: "form",
                    align: "right",
                    label: "Salva e continua le modifiche",
                    {% if not object.pk and not has_add_permission or object.pk and not has_change_permission %}
                        disabled: true,
                    {% endif %}
                    {% if not object.pk and not has_add_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_add_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    {% if object.pk and not has_change_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_change_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    width: 190,
                    click: function () {
                          {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_continue=true' %}
                    }
                },
                {% endif %}
                {% if is_enable_button_save_addanother %}
                {
                    id: '{{ form.webix_id }}_save_addanother',
                    view: "tootipButton",
                    type: "form",
                    align: "right",
                    label: "Salva e aggiungi un altro",
                    {% if not object.pk and not has_add_permission or object.pk and not has_change_permission %}
                    disabled: true,
                    {% endif %}
                    {% if not object.pk and not has_add_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_add_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    {% if object.pk and not has_change_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_change_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    width: 160,
                    click: function () {
                          {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_addanother=true' %}
                    }
                },
                {% endif %}
                {% if is_enable_button_save_gotolist %}
                {
                    id: '{{ form.webix_id }}_save',
                    view: "tootipButton",
                    type: "form",
                    align: "right",
                    label: "Salva",
                    {% if not object.pk and not has_add_permission or object.pk and not has_change_permission %}
                    disabled: true,
                    {% endif %}
                    {% if not object.pk and not has_add_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_add_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    {% if object.pk and not has_change_permission %}
                        tooltip: "{% autoescape off %}{{ info_no_change_permission|join:", " }}{% endautoescape %}",
                    {% endif %}
                    width: 120,
                    click: function () {
                          {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_gotolist=true' %}
                    }
                }
                {% endif %}
            {% endif %}
        {% endblock %}
    ]
});

{# Check toolbar elements number #}
if ($$('main_toolbar_form').getChildViews().length < 2) {
    $$("{{ webix_container_id }}").removeView($$('main_toolbar_form'));
}

{% block form_validate %}
/**
 * Returns if a form is valid
 *
 * @returns {boolean}
 */
function form_validate(webix_id) {
    var form_data_webix_elements = [];
    form_data_webix_elements.push($$(webix_id));

    var status = true;

    $.each(form_data_webix_elements, function (index, value) {
        var valid = value.validate({hidden: true, disabled: true});
        if (valid == false) {
            status = false;
        }
    });

    return status;
}
{% endblock %}
