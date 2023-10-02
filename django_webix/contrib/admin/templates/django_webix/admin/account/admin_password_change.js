{% extends 'django_webix/generic/update.js' %}

{% block extrajs_post %}

$$('id_password1').attachEvent("onSearchIconClick", function (e) {
    const input = this.getInputNode();
    webix.html.removeCss(e.target, "fas fa-eye-slash");
    webix.html.removeCss(e.target, "fas fa-eye");
    if (input.type == "text") {
        webix.html.addCss(e.target, "fas fa-eye");
        input.type = "password";
    } else {
        webix.html.addCss(e.target, "fas fa-eye-slash");
        input.type = "text";
    }
})

$$('id_password2').attachEvent("onSearchIconClick", function (e) {
    const input = this.getInputNode();
    webix.html.removeCss(e.target, "fas fa-eye-slash");
    webix.html.removeCss(e.target, "fas fa-eye");
    if (input.type == "text") {
        webix.html.addCss(e.target, "fas fa-eye");
        input.type = "password";
    } else {
        webix.html.addCss(e.target, "fas fa-eye-slash");
        input.type = "text";
    }
})
{% endblock %}
