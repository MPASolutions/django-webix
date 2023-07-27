{% extends 'django_webix/generic/update.js' %}

{% block extrajs_post %}

function reset(){
    {% with pattern_update_password=urls_namespace|add:':users.user.update_password' %}
    load_js('{% url pattern_update_password object.pk %}', undefined, undefined, undefined,
      undefined,undefined, undefined, abortAllPending=true);
    {% endwith %}
}
{% endblock %}
