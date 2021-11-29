{% load static i18n %}

webix.ui([], $$("{{ webix_container_id }}"));


$$("{{ webix_container_id }}").addView({
    id: 'main_toolbar_navigation',
    view: "toolbar",
    margin: 5,
    cols: [
        {
            view: "template",
            type: "header",
            borderless: true,
            template: '<div style="width:100%; text-align:center;"><strong>{{ _("Password cambiata correttamente")|escapejs }} {{ user }}</strong></div>'
        }
    ]
}, 0);
