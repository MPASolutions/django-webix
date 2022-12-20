{% extends "django_webix/generic/list.js" %}

{% block extrajs_post %}
{{ block.super }}

function command_execute(id) {
    if (id == null) {
        webix.alert({
            title: "{{_("Error")|escapejs}}",
            type: "alert-warning"
        });
    } else {
        $.ajax({
                url: '{% url "dwcommands_manager.commandexecution.execute" pk=0 %}'.replaceAll('0', id),
                method: 'GET',
                success: function (risposta) {
                    webix.message({type: "success", text: "{{_("Started")|escapejs}}"});
                }
            }
        );
    }
}
{% endblock %}
