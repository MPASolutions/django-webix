{% load static tags_agrigis_enogis %}
{
    view: "toolbar",
    cols:[
        {
            align: "left",
            type:"clean",
            template: "<h3 style='margin:4px;'><a style='color:#fff;text-decoration:none;' href='{% url 'admin_webix:index' %}'>{{ title }}</a></h3>",
        },
        {$template: "Spacer"},
        {% comment %}
        //TODO
        {
            view: "icon", align: "right", icon: "fas fa-user", on: {
                onItemClick: function (id, e) {
                    load_js("{% url 'account.update' %}");
                }
            }
        },
           {% endcomment %}
    {% comment %}
        {% if user.is_staff %}
        {
            view: "icon", align: "right", icon: "fas fa-cogs", on: {
                onItemClick: function (id, e) {
                    window.open('/admin/');
                }
            }
        },
        {% endif %}

        {% endcomment %}
        {
            view: "icon", align: "right", icon: "fas fa-sign-out-alt", on: {
                onItemClick: function (id, e) {
                    document.location.href = '{% url 'admin_webix:logout' %}';
                }
            }
        },
    ]
}
