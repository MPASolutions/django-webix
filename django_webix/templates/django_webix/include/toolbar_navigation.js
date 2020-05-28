{% load django_webix_utils i18n %}

$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {% if url_back and url_back != '' %}
            {
                view: "tootipButton",
                type: "base",
                align: "left",
                label: "{{_("Back")|escapejs}}",
                autowidth: true,
                click: function () {
                    load_js("{{ url_back }}", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                }
            },
        {% elif url_list and url_list != '' %}
            {
                view: "tootipButton",
                type: "base",
                align: "left",
                label: "{{_("Back to list")|escapejs}}",
                autowidth: true,
                click: function () {
                    load_js("{{ url_list }}", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                }
            },
        {% endif %}
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>{% if object %}{{ model|getattr:"_meta"|getattr:"verbose_name" }}: {{ object_name|default_if_none:object|escapejs }}{% else %}{{_("Add")|escapejs}} {{ model|getattr:"_meta"|getattr:"verbose_name" }}{% endif %}</strong></div>'
        }
    ]
}, 0);
