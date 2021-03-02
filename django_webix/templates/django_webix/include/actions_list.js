{% load django_webix_utils static i18n %}

{% if is_enable_actions %}

var {{ view_prefix }}actions_list = [
    {% for layer in layers %}
        {id: 'gotowebgis_{{ layer.codename }}', value: "{{_("Go to map")|escapejs}} ({{layer.layername}})"},
    {% endfor %}
    {% for action_key,action in actions.items %}
    {id: '{{ action_key }}', value: '{{action.short_description}}'}{% if not forloop.last %}, {% endif %}
    {% endfor %}
];

{% for action_key,action in actions.items %}
    {% if action.form %}


function _{{ action_key }}_action_execute_form(ids, all) {
  webix.ui({
    view: "window",
    id: "{{ action_key }}_win",
    width: 340,
    maxHeigth: 600,
    scrool: 'y',
    position: "center",
    modal: true,
    move:true,
    resize: true,
    head: {
      view: "toolbar", cols: [
        {view: "label", label: '{{_("Fill in the form")|escapejs}}'},
        {view: "button", label: '{{_("Close")|escapejs}}', width: 100, align: 'right', click: "$$('{{ action_key }}_win').destructor();"}
      ]
    },
    body: {
        view: 'form',
        id: '{{ action.form.webix_id }}',
        name: '{{ action.form.webix_id }}',
        borderless: true,
        elements: [
            {{ action.form.as_webix|safe }},
            {
                id: '{{ action_key }}_toolbar_form',
                view: "toolbar",
                margin: 5,
                cols: [
                    {$template: "Spacer"},
                    {
                        id: '{{ form.webix_id }}_set',
                        view: "tootipButton",
                        type: "form",
                        align: "right",
                        label: "{{_("Go")|escapejs}}",
                        click: function () {
                            if ($$('{{ action.form.webix_id }}').validate({hidden:true, disabled:true})) {
                                webix.extend($$('{{ action.form.webix_id }}'), webix.OverlayBox);
                                $$('{{ action.form.webix_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                _{{ view_prefix }}action_execute(
                                                '{{ action_key }}',
                                                ids,
                                                all,
                                                '{{ action.response_type }}',
                                                '{{ action.short_description }}',
                                                '{{ action.modal_title }}',
                                                '{{ action.modal_ok }}',
                                                '{{ action.modal_cancel }}',
                                                $$('{{ action.form.webix_id }}').getValues(),
                                                function() {$$('{{ action.form.webix_id }}').hideOverlay(); $$('{{ action_key }}_win').destructor()},
                                                function() {$$('{{ action.form.webix_id }}').hideOverlay();}
                                        )
                            }
                        }
                    },
                    {$template: "Spacer"}
                ]
            }
        ],
        rules: {
            {% for field_name, rules in action.form.get_rules.items %}
            '{{ field_name }}': function (value) {
                return {% for r in rules %}{{r.rule}}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} &&
                {% endif %}{% endfor %}
            },
            {% endfor %}
        },
    }
  }).show();
}

    {% endif %}
{% endfor %}


function {{ view_prefix }}actions_execute(action, ids, all) {
    {% for layer in layers %}
    if (action=='gotowebgis_{{ layer.codename }}') {
        $$("map").goToWebgisPks('{{layer.qxsname}}', '{{ pk_field_name }}', ids);
    }
    {% endfor %}
    {% for action_key, action in actions.items %} if (action=='{{ action_key }}') {
        {% if action.form %}
        _{{ action_key }}_action_execute_form(ids,all);
        {% else %}
        _{{ view_prefix }}action_execute(
                '{{ action_key }}',
                ids,
                all,
                '{{ action.response_type }}',
                '{{ action.short_description }}',
                '{{ action.modal_title }}',
                '{{ action.modal_ok }}',
                '{{ action.modal_cancel }}'
        );
        {% endif %}
    } {% if not forloop.last %} else {% endif %} {% endfor %}

}
{% else %}
var {{ view_prefix }}actions_list = undefined;
var {{ view_prefix }}actions_execute = undefined;
{% endif %}
