{% extends 'django_webix/generic/update.js' %}

{% block webix_content %}
{{ block.super }}

{% include "django_webix/commands_manager/common.js" %}

$$('main_toolbar_navigation').addView({
    id:'execute_command',
    view: "button",
    type: "base",
    align: "right",
    label:"{{_("Execute")|escapejs}}",
    autowidth: true,
    click: function () {
        $.ajax(
            {
                url: "{% url "dwcommands_manager.commandexecution.execute" pk=object.id %}",
                method: 'GET',
                success: function (risposta) {
                    webix.message({type: "success", text: "{{_("Started")|escapejs}}"});
                }
            }
        );
    }
})

{% endblock %}
