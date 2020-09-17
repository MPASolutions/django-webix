{% load static %}
{
    view: "toolbar",
    cols:[
        {
            align: "left",
            type:"clean",
            template: "<h3 style='margin:4px;'><a style='color:#fff;text-decoration:none;' href='{% url 'admin_webix:index' %}'>{{ title }}</a></h3>",
        },
        {$template: "Spacer"},
        {
            align: "right",
            type:"clean",
            template: "<span style='color:#fff;font-size: 1.17em;float:right;padding-top:5px;'>{{ user }}</span>",
        },
        {% if user.is_superuser %}
        {
            view: "icon", align: "right", icon: "fas fa-cogs", on: {
                onItemClick: function (id, e) {
                    window.open('/admin/');
                }
            }
        },
        {% endif %}
        {
            view: "icon", align: "right", icon: "fas fa-sign-out-alt", on: {
                onItemClick: function (id, e) {
                    document.location.href = '{% url 'admin_webix:logout' %}';
                }
            }
        },
    ]
}
