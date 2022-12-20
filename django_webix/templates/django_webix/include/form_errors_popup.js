function show_errors(errors) {
    if (errors.length > 0) {
        webix.ui({
            view: "window",
            id: "popup_form_errors_win",
            width: 600,
            height: 400,
            scrool: 'y',
            position: "center",
            modal: true,
            head: {
                view: "toolbar", cols: [
                    {view: "label", label: '{{_("Oops! Something went wrong...")|escapejs}}'},
                    {
                        view: "button",
                        label: '{{_("Close")|escapejs}}',
                        width: 100,
                        align: 'right',
                        click: "$$('popup_form_errors_win').destructor();"
                    }
                ]
            },
            body: {
                rows: [
                    {
                        id: "messages_list",
                        view: "list",
                        type: {height: "auto"},
                        template: function (item) {
                            if (item.label == null)
                                return "<b>" + item.error + "</b></p>";
                            else
                                return "<p style='margin:5px 0px;'><b>" + item.label + "</b>: " + item.error + "</p>";
                        },
                        data: errors
                    },
                ]
            }
        }).show();
    }
}
show_errors(errors);
