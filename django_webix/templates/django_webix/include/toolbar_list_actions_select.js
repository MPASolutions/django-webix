{% load i18n %}

{# actions into select #}
if ((typeof actions_list != 'undefined') && (typeof actions_execute != 'undefined') && (actions_list.length > 0)) {
    var toolbar_actions = [
        {
            view: "richselect",
            id: "action_combo",
            maxWidth: "300",
            minWidth: "200",
            width: "300",
            value: 1,
            labelWidth: 0,
            placeholder: "{%  trans "Select an action" %}...",
            options: actions_list
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
                    prepare_actions_execute(action_name);
                }
            }
        }
    ]
}
