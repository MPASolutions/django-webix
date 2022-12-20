{% extends 'django_webix/admin/base_site.html' %}

{% load static %}
{% if is_app_installed %}
    {% load two_factor %}
{% endif %}

{% block extra_content %}
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
            template: '<div style="width:100%; text-align:center;"><strong>{{ _("Reset password")|escapejs }}</strong></div>'
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
                    template: '{{ _("We have sent instructions for setting the password to the email address you provided. You should receive them shortly as long as the address you entered is valid.")|escapejs }}',
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {
                    view: "template",
                    template: '{{ _("If you do not receive an email, make sure you have entered the address you registered with, and check your spam folder")|escapejs }}',
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {$template: "Spacer", height: 20},
            ]
        },
        {}
    ]
});

{% endblock %}
