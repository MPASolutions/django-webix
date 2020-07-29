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
            template: '<div style="width:100%; text-align:center;"><strong>Reimposta la password</strong></div>'
        }
    ]
}, 0);



$$("{{ webix_container_id }}").addView({
    rows: [
        {
            cols: [
                {$template: "Spacer"},
                {
                    rows: [
                        {$template: "Spacer"},
                        {
                            view: "template",
                            template: "<h2>Password reimpostata</h2>",
                            autoheight: true,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                        {
                            view: "template",
                            template: "La tua password è stata impostata. Ora puoi effettuare l'accesso.",
                            autoheight: true,
                            minWidth: 500,
                            borderless: true,
                            css: {"text-align": 'center'}
                        },
                        {$template: "Spacer"}
                    ]
                },
                {$template: "Spacer"}
            ]
        },

        {
            id: 'main_toolbar_form',
            view: "toolbar",
            css: "webix_dark",
            margin: 5,
            cols: [
                {% if not request.user.is_authenticated %}
                {
                    view: "tootipButton",
                    align: "right",
                    label: "Accedi",
                    width: 160,
                    click: function () {
                        location.href = "{{ login_url }}";
                    }
                },
                {% else %}
                {
                    view: "tootipButton",
                    align: "right",
                    label: "Torna indietro",
                    width: 160,
                    click: function () {
                        location.href = "/";
                    }
                },
                {% endif %}
                {$template: "Spacer"}
            ]
        }
    ]

});
