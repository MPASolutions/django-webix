{% load static %}
{
    view: "toolbar",
    cols:[
        {% if webix_menu_type == 'sidebar' %}
        {
            id:"id_toggle_menu",
            view: "icon",
            icon: "fas fa-bars",
            on: {
                onItemClick: function (id, e) {
                {% if request.user_agent.is_mobile %}
                if ($$("main_menu").isVisible()){
                    $$("main_menu").hide();
                    $$("content_right_vertical").show();
                } else {
                    $$("main_menu").show();
                    $$("content_right_vertical").hide();
                }
                {% else %}
                $$("main_menu").toggle();
                {% endif %}
            }
            }
        },
        {% endif %}
        {% block header_left %}
        {
            id:'id_title',
            align: "left",
            type:"clean",
            {% with pattern_index=urls_namespace|add:':index' %}
            template: "<h3 style='margin:4px;'><a style='color:#fff;text-decoration:none;' href='{% url pattern_index %}'>{{ title }}</a></h3>",
            {% endwith %}
        },
        {$template: "Spacer"},
        {% endblock %}
        {% block header_right %}
        {
            id: "id_title_user",
            align: "right",
            type:"clean",
            template: "<span style='color:#fff;font-size: 1.17em;float:right;padding-top:5px;'>{{ user }}</span>",
        },
        {% endblock %}
        {% if user.is_staff %}
        {
            view: "icon", align: "right", icon: "fas fa-cogs", on: {
                onItemClick: function (id, e) {
                    window.open('/admin/');
                }
            }
        },
        {% endif %}
        {% if is_hijack_enable %}
        {% if request.user.is_hijacked %}
        {
            view: "icon", align: "right", icon: "fas fa-user-times", on: {
                onItemClick: function (id, e) {
                    unhijack_user();
                }
            }
        },
        {% endif %}
        {% endif %}
        {
            view: "icon", align: "right", icon: "fas fa-sign-out-alt", on: {
                onItemClick: function (id, e) {
                    {% with pattern_logout=urls_namespace|add:':logout' %}
                    document.location.href = '{% url pattern_logout %}';
                    {% endwith %}
                }
            }
        },
    ]
}
