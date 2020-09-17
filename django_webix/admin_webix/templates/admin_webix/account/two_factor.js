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
            template: '<div style="width:100%; text-align:center;"><strong>Sicurezza account</strong></div>'
        }
    ]
}, 0);


$$("{{ webix_container_id }}").addView({
    cols: [
        {},
        {
            rows: [
                {$template: "Spacer", height: 20},
                {
                    view: "template",
                    template: "In costruzione",
                    autoheight: true,
                    borderless: true,
                    css: {"text-align": 'center'}
                },
                {$template: "Spacer", height: 20},
            ]
        },
        {}
    ]
});
