{% extends 'auth_webix/base_no_auth.html' %}

{% block webix_content %}
    webix.ui([], $$("{{ webix_container_id }}"));

    {% if 'uid' in request.GET and 'token' in request.GET %}
        load_js("{% url 'auth_webix:password_reset_confirm' uidb64=request.GET.uid token=request.GET.token %}");
    {% else %}
        load_js("{% url "auth_webix:password_reset" %}");
    {% endif %}
{% endblock %}
