{% extends 'django_webix/generic/update.js' %}

{% block extrajs_post %}

function reset(){
    load_js('{% url "dwadmin:users.user.update_password" object.pk %}', undefined, undefined, undefined,
      undefined,undefined, undefined, abortAllPending=true);
}
{% endblock %}
