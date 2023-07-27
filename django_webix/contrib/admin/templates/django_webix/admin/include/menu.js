{% load static django_webix_admin_utils %}
{
    id:'main_menu',
    width: {{ webix_menu_width }},
    view:"{{ webix_menu_type }}",
    openAction:"click",
    {% if webix_menu_type == 'menu' %}
    type:{
        subsign: true
    },
    {% endif %}
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
            {% with pattern_index=urls_namespace|add:':index' %}
            url: '{% url pattern_index %}'
            {% endwith %}
        },
        {# START EXTRA MENU PREVIUS #}
        {% block extra_menu_previus %}
        {% endblock %}
        {# END EXTRA MENU PREVIUS #}

        {% block userprofile %}
        {% if not disable_userprofile %}
        {
            id: 'menu_user{{ disable_userprofile }}',
            value: "{{ _("User")|escapejs }}",
            icon: "fas fa-user",
            {% if webix_menu_type == 'sidebar' %}data{% else %}submenu{% endif %}: [
                {
                    id: 'menu_profile_update',
                    value: "{{ _("Profile")|escapejs }}",
                    icon: "fas fa-user-edit",
                    loading_type: 'js_script',
                    {% with pattern_account_update=urls_namespace|add:':account_update' %}
                    url: "{% url pattern_account_update %}"
                    {% endwith %}
                },
                {
                    id: 'menu_profile_change_password',
                    value: "{{ _("Password change")|escapejs }}",
                    icon: "fas fa-key",
                    loading_type: 'js_script',
                    {% with pattern_password_change=urls_namespace|add:':password_change' %}
                    url: "{% url pattern_password_change %}"
                    {% endwith %}
                },
                {
                    id: 'menu_profile_reset_password',
                    value: "{{ _("Password reset")|escapejs }}",
                    icon: "fas fa-mail-bulk",
                    loading_type: 'js_script',
                    {% with pattern_password_reset=urls_namespace|add:':password_reset' %}
                    url: "{% url pattern_password_reset %}"
                    {% endwith %}
                },
                {% if 'two_factor'|is_app_installed %}
                {
                    id: 'menu_profile_two_factor',
                    value: "{{ _("2 factor authentication")|escapejs }}",
                    icon: "fas fa-shield-alt",
                    loading_type: 'js_script',
                    {% with pattern_two_factor_profile=urls_namespace|add:':two_factor_profile' %}
                    url: "{% url pattern_two_factor_profile %}"
                    {% endwith %}
                }
                {% endif %}
            ]
        },
        {% endif %}
        {% endblock %}

        {% block users %}
        {% if not disable_users %}
        {% if user.is_superuser and user_list_url %}
        {
            id: 'menu_profile',
            value: "{{ _("Manage users")|escapejs }}",
            icon: "fas fa-users",
            {% if webix_menu_type == 'sidebar' %}data{% else %}submenu{% endif %}: [
                {
                    id: 'menu_users',
                    value: "{{ _("Users")|escapejs }}",
                    icon: "fas fa-users",
                    loading_type: 'js_script',
                    url: "{% url user_list_url %}"
                },
            ]
        },
        {% endif %}
        {% endif %}
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
        {% if webix_menu_type == 'sidebar' %}onAfterSelect{% else %}onMenuItemClick{% endif %}: function (id) {
            {% if is_webgis_enable %}
            $$('map').enableDataTab();
            {% endif %}
            item = this.{% if webix_menu_type == 'sidebar' %}getItem{% else %}getMenuItem{% endif %}(id);
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
