{% load django_webix_utils %}

function get_ids_input_prefix(empty_form, totalForms) {
    var ids = []
    $.each(empty_form.getChildViews(), function (i, el) {
        ids = ids.concat(get_ids_input_prefix(el, totalForms));
        if ((el.config !== undefined) && (el.config.name !== undefined) && (el.config.id !== undefined)) { // name only for input items
            new_id = el.config.id.replace("__prefix__", '' + totalForms);
            ids.push(new_id);
        }
    });
    return ids
}

/**
 * Returns a copy of the empty form with an integer id instead of __prefix__
 *
 * @param empty_form
 * @param totalForms integer
 * @param form_id [Optional]
 * @returns {Array} new inline form
 */
function create_inline(empty_form, totalForms, form_id) {
    // duplicate form from empty_form
    var new_config = JSON.parse(JSON.stringify(empty_form.config).split("__prefix__").join('' + totalForms));
    new_config.__proto__ = undefined;
    new_config.hidden = false;
    if ((empty_form.config.header!=undefined)&&(empty_form.config.header!=false)) { // only for stacked
        new_config.header = empty_form.config.header(); // it's a function!
    }
    new_config.id = new_config.id.replace('empty_form', totalForms + '-inline');
    $$(form_id).addView(new_config);
    // rule
    var fields_ids = get_ids_input_prefix(empty_form, totalForms);
    $.each(fields_ids, function (i, field_id) {
        add_rule(field_id);
    })
}


/**
 * Function to add rules to input fields on change
 *
 * @param field_id field id to add onChange event
 */
function add_rule(field_id) {
    if ($$(field_id)==undefined){
        console.log('Config field error',field_id);
    }
    $$(field_id).attachEvent("onChange", function () {
        var prefix = /^id_(.*)-\d+-.*$/.exec(this.config.id)[1];

        // add all rules that start with prefix-__prefix__- and replace __prefix__ with inline number
        var rules = findValueByPrefix(_prefix_rules, prefix + "-__prefix__-");
        for (var rule in rules) {
            var regex = /^.*-(\d+)-.*$/;
            var match = regex.exec(this.config.id);
            var new_key = rule.replace('__prefix__', match[1]);

            // this.getValue() === "2" because is already checked
            if (this.config.id.match("-DELETE$") && this.getValue() === "2" && new_key in $$("{{ form.webix_id }}").config.rules) {
                // Rimuovo le regole
                delete $$("{{ form.webix_id }}").config.rules[new_key]
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


function delete_image(webix_id_block, webix_id_button) {
    // ho messo un timeout perche il click avviene prima del change del toogle...
    setTimeout(function () {
        if ($$(webix_id_button) != undefined && $$(webix_id_block) != undefined) {
            if ($$(webix_id_button).getValue() == 1) {
                webix.html.addCss($$(webix_id_block).getNode(), "deleted-inline");
            } else {
                webix.html.removeCss($$(webix_id_block).getNode(), "deleted-inline");
            }
        }
    }, 100);
}


function image_add(uploader_id) {
    //console.log('ci siamo');
    //console.log(uploader_id)
}
