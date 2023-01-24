function show_errors(errors) {
    var li_text_errors = '';
    errors.forEach(function (item, index) {
        if (item.label!=null) {
            li_text_errors += "<li><b>" + item.label + "</b>: " + item.error + "</li>"
        } else {
            li_text_errors += "<li>" + item.error + "</li>"
        }
        });
    if (errors.length > 0) {
        webix.message({
            type: "error",
            text: "{{_("Oops! Something went wrong...")|escapejs}}" +
                "<br><br>" +
                "{{_("Error in the following fields:")|escapejs}}" +
                "<ul>" +
                li_text_errors +
                "</ul>"
        });
    }
}
show_errors(errors);
