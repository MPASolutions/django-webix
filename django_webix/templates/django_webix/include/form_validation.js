{% load i18n %}

/**
 * Returns if a field required is not empty
 *
 * @param field_name
 * @param value
 * @returns {boolean}
 */
function isNotEmpty(field_name, value) {
    $$("id_" + field_name).define("tooltip", '{% trans "Required field" %}');
    return value != null && value !== '';
}

/**
 * Returns if a field contains an email address
 *
 * @param field_name
 * @param value
 * @returns {*}
 */
function isEmail(field_name, value) {
    $$("id_" + field_name).define("tooltip", '{% trans "Invalid email" %}');
    var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
    if (value == null || value === '')
        return true;
    return re.test(value);
}

/**
 * Returns if a field contains an integer
 *
 * @param value
 * @returns {*}
 */
function isInt(value) {
    if (value == undefined) {
        return true;
    }
    else if (String(value).indexOf('.') >= 0 || String(value).indexOf(',') >= 0) {
        return false;
    }
    return ($.isNumeric(value) && Math.floor(value) === Number(value));
}

/**
 * Returns if a field contains an integer and checks if it's inside the min/max range
 *
 * @param field_name
 * @param value
 * @param max
 * @param min
 * @returns {boolean}
 */
function isInteger(field_name, value, max, min) {
    // TODO
    if (value !== '') {
        if (isInt(value) === false) {
            $$("id_" + field_name).define("tooltip", 'Campo non intero');
            return false;
        }
        if (Number(value) < Number(min)) {
            $$("id_" + field_name).define("tooltip", 'Valore minore di ' + min);
            return false;
        }
        if (Number(value) > Number(max)) {
            $$("id_" + field_name).define("tooltip", 'Valore maggiore di ' + max);
            return false;
        }
    }
    return true;
}

/**
 * Returns if a field contains a number and checks if it's inside the min/max range
 *
 * @param field_name
 * @param value
 * @param max
 * @param min
 * @returns {boolean}
 */
function isNumber(field_name, value, max, min) {
    if (!$.isNumeric(value)) {
        value = value.replace(',', '.');
    }
    value = Number(value);

    if (isNaN(value) || value === undefined) {
        return true;
    }
    if (value !== '' && value !== parseFloat(value)) {
        $$("id_" + field_name).define("tooltip", 'Campo non decimale');
        return false;
    }
    if (value < min) {
        $$("id_" + field_name).define("tooltip", 'Valore minore di ' + min);
        return false;
    }
    if (value > max) {
        $$("id_" + field_name).define("tooltip", 'Valore maggiore di ' + max);
        return false;
    }
    return true;
}

/**
 * Returns if a field contains a string and checks it's length
 *
 * @param field_name
 * @param value
 * @param max
 * @param min
 * @returns {boolean}
 */
function isString(field_name, value, max, min) {
    if (value !== null) {
        if (value.length < min) {
            $$("id_" + field_name).define("tooltip", 'Stringa più corta di ' + min);
            return false;
        }
        if (value.length > max) {
            $$("id_" + field_name).define("tooltip", 'Stringa più lunga di ' + max);
            return false;
        }
    }
    return true;
}
