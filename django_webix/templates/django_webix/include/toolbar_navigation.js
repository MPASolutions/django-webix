{% load django_webix_utils i18n %}

{% if request.user_agent.is_mobile %}
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
                label: '<div title="{{_("Back")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-step-backward"></i></div>',
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
                label: '<div title="{{_("Back to list")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-step-backward"></i></div>',
                autowidth: true,
                click: function () {
                    load_js("{{ url_list|safe }}{% if not '?' in url_list %}?{% else %}&{% endif %}full_state", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                }
            },
        {% endif %}
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>{% if object %}{{ object_name|default:object|escapejs }}{% else %}{{_("Add")|escapejs}} {{ model|getattr:"_meta"|getattr:"verbose_name" }}{% endif %}</strong></div>'
        },
        {% if object.pk %}
            {% for layer in layers %}
                 {
                    view: "tootipButton",
                    {% if not object|getattr:layer.geofieldname %}
                    disabled:true,
                    tooltip: "{{_("Geometry does not exist")|escapejs}}",
                    {% endif %}
                    type: "base",
                    align: "left",
                    label: '<div title="{{_("Go to map")|escapejs}} ({{layer.layername}})"><i style="cursor:pointer" class="webix_icon far fa-map"></i></div>',
                    autowidth: true,
                    click: function () {
                        $$("map").goToWebgisPk('{{layer.qxsname}}', '{{ pk_field_name }}', {{ object.pk }});
                    }
                },
            {% endfor %}
        {% endif %}
    ]
}, 0);

{% else %}
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
                    load_js("{{ url_list|safe }}{% if not '?' in url_list %}?{% else %}&{% endif %}full_state", undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
                }
            },
        {% endif %}
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>{% if object %}{{ model|getattr:"_meta"|getattr:"verbose_name" }}: {{ object_name|default:object|escapejs }}{% else %}{{_("Add")|escapejs}} {{ model|getattr:"_meta"|getattr:"verbose_name" }}{% endif %}</strong></div>'
        },
        {% if object.pk %}
            {% for layer in layers %}
                 {
                    view: "tootipButton",
                    {% if not object|getattr:layer.geofieldname %}
                    disabled:true,
                    tooltip: "{{_("Geometry does not exist")|escapejs}}",
                    {% endif %}
                    type: "base",
                    align: "left",
                    label: "{{_("Go to map")|escapejs}} ({{layer.layername}})",
                    autowidth: true,
                    click: function () {
                        $$("map").goToWebgisPk('{{layer.qxsname}}', '{{ pk_field_name }}', {{ object.pk }});
                    }
                },
            {% endfor %}
        {% endif %}
    ]
}, 0);
{% endif %}
