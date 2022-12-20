/**
 * Returns if a form is valid
 *
 * @returns {boolean}
 */
function form_validate(webix_id) {
    var form_data_webix_elements = [];
    form_data_webix_elements.push($$(webix_id));

    var status = true;

    $.each(form_data_webix_elements, function (index, value) {
        var valid = value.validate({hidden: true, disabled: true});
        if (valid == false) {
            status = false;
        }
    });

    return status;
}
