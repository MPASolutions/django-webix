{% load django_webix_utils i18n %}

{% block webix_content %}

{% block context_cleaner %}
webix.ui([], $$("{{ webix_container_id }}"));
{% endblock %}


{% block form_standard %}
{% include "django_webix/include/form_standard.js" %}
{% endblock %}

{% block toolbar_form %}

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_form',
    view: "toolbar",
    margin: 5,
    cols: [
        {
            id: '{{ form.webix_id }}_send',
            view: "tootipButton",
            type: "form",
            align: "right",
            label: "{{_("Send")|escapejs}}",
            width: 90,
            click: function () {
                {% block click_send %}
                {% include "django_webix/include/toolbar_form_save.js"%}
                {% endblock %}
            }
        },
        {}
    ]
});

{% endblock %}

{% block form_validate %}
{% include "django_webix/include/toolbar_form_validate.js" %}
{% endblock %}

{% block extrajs_post %}{% endblock %}
{% endblock %}
