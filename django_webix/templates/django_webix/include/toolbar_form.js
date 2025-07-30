{% load django_webix_utils static i18n %}


$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    height: 32,
    cols: [
        {% block button_delete %}
                {% if object.pk  and url_delete and url_delete != '' %}
                    {
                        id: '{{ form.webix_id }}_delete',
                        view: "tootipButton",
                        type: "danger",
                        css: "webix_danger",
                        align: "left",
                        label: '{% if request.user_agent.is_mobile %}<div title="{{_("Delete")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-trash"></i></div>{% else %}{{_("Delete")|escapejs}}{% endif %}',
                        {% if not has_delete_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_delete_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% endif %}
                        width: {% if request.user_agent.is_mobile %}40{% else %}120{% endif %},
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
                        label: '{% if request.user_agent.is_mobile %}<div title="{{_("Save and continue")|escapejs}}"><i style="cursor:pointer" class="webix_icon fal fa-file-download"></i><i style="cursor:pointer" class="webix_icon fal fa-redo-alt"></i></div>{% else %}{{_("Save and continue")|escapejs}}{% endif %}',
                        width: {% if request.user_agent.is_mobile %}60{% else %}190{% endif %},
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_add_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% elif object.pk and not has_change_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_change_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% endif %}
                        click: function () {
                              webix.storage.local.put("last_button_click", '{{ form.webix_id }}_save_continue');
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
                        label: '{% if request.user_agent.is_mobile %}<div title="{{_("Save and add another")|escapejs}}"><i style="cursor:pointer" class="webix_icon fal fa-file-download"></i><i style="cursor:pointer" class="webix_icon fas fa-plus"></i></div>{% else %}{{_("Save and add another")|escapejs}}{% endif %}',
                        width: {% if request.user_agent.is_mobile %}60{% else %}260{% endif %},
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_add_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% elif object.pk %}
                            {% if not has_change_permission or not has_add_permission %}
                                {% if remove_disabled_buttons %} hidden: true, {% endif %}
                                disabled: true,
                                tooltip: "{% for i in info_no_change_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                            {% endif %}
                        {% endif %}
                        click: function () {
                              webix.storage.local.put("last_button_click", '{{ form.webix_id }}_save_addanother');
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
                        label: '{% if request.user_agent.is_mobile %}<div title="{{_("Save")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-file-download"></i><i style="cursor:pointer" class="webix_icon far fa-list"></i></div>{% else %}{{_("Save")|escapejs}}{% endif %}',
                        width: {% if request.user_agent.is_mobile %}60{% else %}120{% endif %},
                        {% if not object.pk and not has_add_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_add_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% elif object.pk and not has_change_permission %}
                            {% if remove_disabled_buttons %} hidden: true, {% endif %}
                            disabled: true,
                            tooltip: "{% for i in info_no_change_permission %}{{ i|escapejs }}{% if not forloop.last %}, {% endif %}{% endfor %}",
                        {% endif %}
                        click: function () {
                            webix.storage.local.put("last_button_click", '{{ form.webix_id }}_save');
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
