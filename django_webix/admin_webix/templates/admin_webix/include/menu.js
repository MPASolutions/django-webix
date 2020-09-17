{% load static django_webix_admin_utils %}
{
    id:'main_menu',
    width: 180,
    view:"menu",
    openAction:"click",
    type:{
        subsign: true
    },
    scroll:"y",
    layout: "y",
    subMenuPos:"right",
    submenuConfig:{
        width: 255,
        zIndex:1000
    },
    data: [
        {
            id: 'menu_homepage',
            value: "Home",
            icon: "fas fa-home",
            loading_type: 'redirect',
            url: '{% url 'admin_webix:index' %}'
        },
        {# START EXTRA MENU PREVIUS #}
        {% block extra_menu_previus %}
        {% endblock %}
        {# END EXTRA MENU PREVIUS #}

        {% block userprofile %}
        {
            id: 'menu_profile',
            value: "Utente",
            icon: "fas fa-user",
            submenu: [
                {
                    id: 'menu_profile_update',
                    value: "Il mio profilo",
                    icon: "fas fa-user-edit",
                    loading_type: 'js_script',
                    //url: 'account/update/' + "{{ user.pk }}"
                    url: "{% url 'admin_webix:account_update' user.pk %}"
                },
                {
                    id: 'menu_profile_change_password',
                    value: "Cambia password",
                    icon: "fas fa-key",
                    loading_type: 'js_script',
                    url: "{% url 'admin_webix:password_change' %}"
                },
                {
                    id: 'menu_profile_reset_password',
                    value: "Reimposta password",
                    icon: "fas fa-mail-bulk",
                    loading_type: 'js_script',
                    url: "{% url 'admin_webix:password_reset' %}"
                },
                {% if 'two_factor'|is_app_installed %}
                {
                    id: 'menu_profile_two_factor',
                    value: "Autenticazione a 2 fattori",
                    icon: "fas fa-shield-alt",
                    loading_type: 'js_script',
                    url: "{% url 'admin_webix:two_factor_profile' %}"
                }
                {% endif %}
            ]
        },
        {% endblock %}

        {% for menu_item in menu_list %}
        {{ menu_item|safe }},
        {% endfor %}

        {# START EXTRA MENU AFTER #}
        {% block extra_menu_after %}
        {% endblock %}
        {# END EXTRA MENU AFTER #}
    ],
    on:{
        onMenuItemClick: function (id) {
            {% if is_webgis_enable %}
            $$('map').enableDataTab();
            {% endif %}
            item = this.getMenuItem(id);
            loading_type = item.loading_type;
            url = item.url;
            if (loading_type == 'redirect') {
                loading(url);
            } else if (loading_type == 'js_script') {
                load_js(url);
            }
        }
    }
}
