{% load i18n %}

{# actions on buttons #}
var {{ view_prefix }}toolbar_actions = [];
$.each({{ view_prefix }}actions_list, function (index, obj) {
    {{ view_prefix }}toolbar_actions.push({
        view: "tootipButton",
        autowidth: true,
        id: 'action_' + obj.id,
        value: '' + obj.value,
        click: function () {
            {{ view_prefix }}prepare_actions_execute(obj.id);
        }
    });
});
