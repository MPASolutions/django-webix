{% load static %}

{% block webix_content %}
    webix.ui([], $$("{{ webix_container_id }}"));

    $$("{{ webix_container_id }}").addView({
        cols: [
            {$template: "Spacer"},
            {
                rows: [
                    {$template: "Spacer"},
                    {% block content_extra_top %}{% endblock %}
                    {% block password_reset_title %}
                        {
                            view: "template",
                            template: "<h2>{{ title }}</h2>",
                            minWidth: 500,
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_instructions %}
                        {
                            view: "template",
                    template: '{{ _("We have sent instructions for setting the password to the email address you provided. You should receive them shortly as long as the address you entered is valid.")|escapejs }}',
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_spam %}
                        {
                            view: "template",
                    template: '{{ _("If you do not receive an email, make sure you have entered the address you registered with, and check your spam folder")|escapejs }}',
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                    {% endblock %}
                    {% block password_reset_back %}
                        {
                            view: "form",
                            borderless: true,
                            elements: [
                                {
                                    view: "button",
                                    css: "webix_transparent",
                                    value: "{{ _("Go back to the home page")|escapejs }}",
                                    click: function () {
                                        location.href = "/";
                                    }
                                }
                            ]
                        },
                    {% endblock %}
                    {% block content_extra_bottom %}{% endblock %}
                    {$template: "Spacer"}
                ]
            },
            {$template: "Spacer"}
        ]
    });
{% endblock %}
