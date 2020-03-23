{% load i18n %}

{# actions on buttons #}
var toolbar_actions = [];
$.each(actions_list, function (index, obj) {
    toolbar_actions.push({
        view: "tootipButton",
        autowidth: true,
        id: 'action_' + obj.id,
        value: '' + obj.value,
        click: function () {
            prepare_actions_execute(obj.id);
        }
    });
});
