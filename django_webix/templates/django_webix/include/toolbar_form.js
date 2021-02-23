{% load django_webix_utils static i18n %}


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
                        label: "{{_("Delete")|escapejs}}",
                        {% if not has_delete_permission %}
                            disabled: true,
                            tooltip: "{{ info_no_delete_permission|join:", "|escapejs }}",
                        {% endif %}
                        width: 120,
                        click: function () {
                            load_js("{{ url_delete }}", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
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
                        label: "{{_("Save and continue")|escapejs}}",
                        {% if not has_change_permission %}
                            disabled: true,
                        {% elif not object.pk and not has_add_permission %}
                            disabled: true,
                        {% elif object.pk and not has_change_permission %}
                            disabled: true,
                        {% endif %}
                        {% if not object.pk and not has_add_permission %}
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs}}",
                        {% endif %}
                        {% if object.pk and not has_change_permission %}
                            tooltip: "{{ info_no_change_permission|join:", "|escapejs}}",
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
                        label: "{{_("Save and add another")|escapejs}}",
                        {% if not has_add_permission %}
                            disabled: true,
                        {% elif not object.pk and not has_add_permission %}
                            disabled: true,
                        {% elif object.pk and not has_change_permission %}
                            disabled: true,
                        {% endif %}
                        {% if not object.pk and not has_add_permission %}
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs}}",
                        {% endif %}
                        {% if object.pk and not has_change_permission %}
                            tooltip: "{{ info_no_change_permission|join:", "|escapejs}}",
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
                        label: "{{_("Save")|escapejs}}",
                        {% if not has_view_permission %}
                            disabled: true,
                        {% elif not object.pk and not has_add_permission %}
                            disabled: true,
                        {% elif object.pk and not has_change_permission %}
                            disabled: true,
                        {% endif %}
                        {% if not object.pk and not has_add_permission %}
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs }}",
                        {% endif %}
                        {% if object.pk and not has_change_permission %}
                            tooltip: "{{ info_no_change_permission|join:", "|escapejs }}",
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
  {% include "django_webix/include/toolbar_form_validate.js" %}
{% endblock %}
