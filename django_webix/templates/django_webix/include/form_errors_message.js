function show_errors(errors) {
    var li_text_errors = '';
    // check if is an array of strings or array of dicts
    if (errors.length > 0){
        if (typeof errors[0] === "string") {
            errors.forEach(function (txt_error) {
                li_text_errors += "<li><b>" + txt_error + "</b>"
            });
        } else {
            errors.forEach(function (item, index) {
                if (item.label!=null) {
                    li_text_errors += "<li><b>" + item.label + "</b>: " + item.error + "</li>"
                } else {
                    li_text_errors += "<li>" + item.error + "</li>"
                }
            });
        }
        webix.message({
            type: "error",
            expire: 10000,
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
