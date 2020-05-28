{% load i18n %}

{# actions into select #}
if ((typeof {{ view_prefix }}actions_list != 'undefined') && (typeof {{ view_prefix }}actions_execute != 'undefined') && ({{ view_prefix }}actions_list.length > 0)) {
    var {{ view_prefix }}toolbar_actions = [
        {
            view: "richselect",
            id: "action_combo",
            maxWidth: "300",
            minWidth: "200",
            width: "300",
            value: 1,
            labelWidth: 0,
            placeholder: "{%  trans "Select an action" %}...",
            options: {{ view_prefix }}actions_list
        },
        {
            view: "tootipButton",
            id: "action_button",
            value: "{%  trans "Go" %}",
            inputWidth: 60,
            width: 60,
            on: {
                onItemClick: function () {
                    var action_name = $$("action_combo").getValue();
                    {{ view_prefix }}prepare_actions_execute(action_name);
                }
            }
        }
    ]
}
