{% load django_webix_utils static i18n %}


$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    cols: [
        {% block button_delete %}
                {% if object.pk  and url_delete and url_delete != '' %}
                    {
                        id: '{{ form.webix_id }}_delete',
                        view: "tootipButton",
                        type: "danger",
                        css: "webix_danger",
                        align: "left",
                        label: "{{_("Delete")|escapejs}}",
                        {% if not has_delete_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_delete_permission|join:", "|escapejs }}",
                        {% endif %}
                        width: 120,
                        click: function () {
                            load_js("{{ url_delete|safe }}", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                        }
                    },
                {% endif %}
        {% endblock %}
        {% block extra_buttons_left %}{% endblock %}
        {$template: "Spacer"},
        {% block extra_buttons_right %}{% endblock %}
        {% block button_save %}
                // is_enable_button_save_continue
                {% if is_enable_button_save_continue %} // true
                    {
                        id: '{{ form.webix_id }}_save_continue',
                        view: "tootipButton",
                        type: "form",
                        css:"webix_secondary",
                        align: "right",
                        label: "{{_("Save and continue")|escapejs}}",
                        width: 190,
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs}}",
                        {% elif object.pk and not has_change_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_change_permission|join:", "|escapejs}}",
                        {% endif %}
                        click: function () {
                              {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_continue=true' %}
                        }
                    },
                {% endif %}
                // is_enable_button_save_addanother
                {% if is_enable_button_save_addanother %} // true
                    {
                        id: '{{ form.webix_id }}_save_addanother',
                        view: "tootipButton",
                        type: "form",
                        css:"webix_secondary",
                        align: "right",
                        label: "{{_("Save and add another")|escapejs}}",
                        width: 260,
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs}}",
                        {% elif object.pk %}
                            {% if not has_change_permission or not has_add_permission %}
                                {% if remove_disabled_buttons %} hidden: true, {% endif %}
                                disabled: true,
                                tooltip: "{{ info_no_change_permission|join:", "|escapejs}}",
                            {% endif %}
                        {% endif %}
                        click: function () {
                              {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_addanother=true' %}
                        }
                    },
                {% endif %}
                // is_enable_button_save_gotolist
                {% if is_enable_button_save_gotolist %} // true
                    {
                        id: '{{ form.webix_id }}_save',
                        view: "tootipButton",
                        type: "form",
                        css:"webix_primary",
                        align: "right",
                        label: "{{_("Save")|escapejs}}",
                        width: 120,
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_add_permission|join:", "|escapejs }}",
                        {% elif object.pk and not has_change_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{{ info_no_change_permission|join:", "|escapejs }}",
                        {% endif %}
                        click: function () {
                              {% include "django_webix/include/toolbar_form_save.js" with extra_params_button='_gotolist=true' %}
                        }
                    }
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
