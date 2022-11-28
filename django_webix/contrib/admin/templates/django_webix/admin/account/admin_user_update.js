{% extends 'django_webix/generic/update.js' %}

{% block extrajs_post %}

function reset(){
    load_js('{% url "admin_webix:admin_webix_password_change_admin" object.pk %}', undefined, undefined, undefined,
      undefined,undefined, undefined, abortAllPending=true);
}
{% endblock %}
