/**
 * Returns a copy of the empty form with an integer id instead of __prefix__
 *
 * @param empty_form
 * @param totalForms
 * @param form_id [Optional]
 * @returns {Array} new inline form
 */
function replace_prefix(empty_form, totalForms, form_id) {
    var new_form = [];
    $.each(empty_form, function (i, el) {
        var new_el = webix.clone(el.config);

        if (new_el.cols !== undefined) {
            new_el.cols = replace_prefix(el.getChildViews(), totalForms);
        } else {
            if (el.config.id !== undefined)
                new_el.id = new_el.id.replace("__prefix__", totalForms.getValue());
            if (el.config.name !== undefined)
                new_el.name = new_el.name.replace("__prefix__", totalForms.getValue());
        }

        if (form_id !== undefined) {
            $$(form_id).addView(new_el);
            add_rule(new_el.id);
        }

        new_form.push(new_el);
    });

    return new_form;
}


/**
 * Function to add rules to input fields on change
 *
 * @param field_id field id to add onChange event
 */
function add_rule(field_id) {
    $$(field_id).attachEvent("onChange", function () {
        var prefix = /^id_(.*)-\d+-.*$/.exec(this.config.id)[1];

        // Aggiungo tutte le regole che iniziano con prefix-__prefix__- e sostituisco __prefix__ con il numero dell'inline
        var rules = findValueByPrefix(_prefix_rules, prefix + "-__prefix__-");
        for (var rule in rules) {
            var regex = /^.*-(\d+)-.*$/;
            var match = regex.exec(this.config.id);
            var new_key = rule.replace('__prefix__', match[1]);

            // this.getValue() === "2" because is already checked
            if (this.config.id.match("-DELETE$") && this.getValue() === "2" && new_key in $$("{{ form.webix_id }}").config.rules) {
                // Rimuovo le regole
                delete  $$("{{ form.webix_id }}").config.rules[new_key]
            } else {
                // Aggiungo le regole
                $$("{{ form.webix_id }}").config.rules[new_key] = rules[rule];
            }
        }
    })
}


/**
 * Function to add delete event
 *
 * @param prefix inline prefix to add delete click event to delete an inline
 */
function delete_trigger(prefix) {
    $$(prefix + "-DELETE-icon").attachEvent("onItemClick", function () {
        if ($$("id_" + prefix + "-DELETE").getValue() === "") {
            webix.html.addCss($$(prefix + "-inline").getNode(), "deleted-inline");
            $$("id_" + prefix + "-DELETE").setValue("2");
        } else {
            webix.html.removeCss($$(prefix + "-inline").getNode(), "deleted-inline");
            $$("id_" + prefix + "-DELETE").setValue("");
        }
    });
}


/**
 * Returns a dict with inline rules
 *
 * @param object
 * @param prefix
 */
function findValueByPrefix(object, prefix) {
    var result = {}
    for (var property in object) {
        if (object.hasOwnProperty(property) && property.toString().match("^" + prefix)) {
            result[property] = object[property]
        }
    }
    return result;
}
