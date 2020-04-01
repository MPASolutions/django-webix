{% load static tags_agrigis_enogis %}
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
    {% for item_app in available_apps %}
        {
            id: 'menu_{{item_app.app_label}}',
            value: "{{ item_app.name }}",
            icon: "fas fa-archive",
            submenu: [
            {% for item_model in item_app.models %}
                {
                    id: 'menu_{{item_app.app_label}}_{{ item_model.model_name }}',
                    value: "{{ item_model.name }}",
                    icon: "far fa-archive",
                    loading_type: 'js_script',
                    url: '{{ item_model.admin_url }}'
                }{% if not forloop.last %},{% endif %}
            {% endfor %}
            ]
        }{% if not forloop.last %},{% endif %}
    {% endfor %}


        {# START BLOCCO EXTRA #}
        {% block extra_menu %}
        {% endblock %}
        {# END BLOCCO EXTRA #}
    ],
    on:{
        onMenuItemClick: function (id) {
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
