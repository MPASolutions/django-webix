{% load static django_webix_utils i18n %}

{# csrf set and abort all using jQuery #}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.xhrPool = [];
$.xhrPoolAbortAll = function () {
    $.xhrPool.forEach(function (xhr) {
        xhr.abort();
    });
    $.xhrPool = [];
};

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        $.xhrPool.push(xhr);
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            var csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    },
    complete: function (xhr) {
        var index = $.xhrPool.indexOf(xhr);
        if (index > -1) {
            $.xhrPool.splice(index, 1);
        }
    }
});

{# csrf set webix #}

webix.attachEvent("onBeforeAjax", function (mode, url, data, xhr, headers) {
    var csrftoken = getCookie('csrftoken');
    headers["X-CSRFToken"] = csrftoken;
});

{# Italian locale settings for pivot #}

webix.i18n.locales['it-IT'].pivot = {
    apply: "Applica",
    cancel: "Annulla",
    columns: "Colonne",
    count: "Somma",
    fields: "Campi",
    filters: "Filtri",
    max: "max",
    min: "min",
    operationNotDefined: "Operazione non definita",
    pivotMessage: "Clicca per personalizzare",
    rows: "Righe",
    select: "selezione",
    sum: "somma",
    text: "testo",
    values: "Valori",
    windowTitle: "Configurazione",
    windowMessage: "[Trascinare i campi di sinistra nella sezione desiderata]",
    total: "Totale"
};

{# values casts #}

function isNumberCheck(val) {
    if (val.match(/^\d+\.\d+$/) || val.match(/^\d+\,\d+$/) || val.match(/^-{0,1}\d+$/)) {
        return true;
    } else {
        return false;
    }
}

{# templates lists #}

function custom_checkbox(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == '0') || (value === 0) || (value === false))
        return "<img style='width:12px;' src='{% static 'admin/img/icon-no.svg' %}'> "
    else if ((value == 'True') || (value == 'true') || (value == '1') || (value === 1) || (value === true))
        return "<img style='width:12px;' src='{% static 'admin/img/icon-yes.svg' %}'> "
    else
        return "<img style='width:12px;' src='{% static 'admin/img/icon-unknown.svg' %}'> "
}

function custom_checkbox_pointer(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == '0') || (value === 0) || (value === false))
        return "<img style='width:12px;cursor:pointer' src='{% static 'admin/img/icon-no.svg' %}'> "
    else if ((value == 'True') || (value == 'true') || (value == '1') || (value === 1) || (value === true))
        return "<img style='width:12px;cursor:pointer' src='{% static 'admin/img/icon-yes.svg' %}'> "
    else
        return "<img style='width:12px;cursor:pointer' src='{% static 'admin/img/icon-unknown.svg' %}'> "
}

function custom_checkbox_help(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == '0') || (value === 0) || (value === false))
        return "<img style='width:12px;cursor:help' src='{% static 'admin/img/icon-no.svg' %}'> "
    else if ((value == 'True') || (value == 'true') || (value == '1') || (value === 1) || (value === true))
        return "<img style='width:12px;cursor:help' src='{% static 'admin/img/icon-yes.svg' %}'> "
    else
        return "<img style='width:12px;cursor:help' src='{% static 'admin/img/icon-unknown.svg' %}'> "
}

function custom_checkbox_yesno(obj, common, value) {
    if (value)
        return "<div style='color:green;'>{{_("Yes")|escapejs}}</div>";
    else
        return "<div style='color:red;'>{{_("No")|escapejs}}</div>";
}

function custom_checkbox_default(obj, common, value) {
    if (value)
        return '<div title="{{_("Default")|escapejs}}"><i style="cursor:pointer" class="webix_icon fas fa-check-circle"></i></div>';
    else
        return ''
}

function custom_button_geo(obj, common, value) {
    if (value)
        return '<div title="{{_("Show on map")|escapejs}}"><i style="cursor:pointer" class="webix_icon fas fa-map-marker-alt"></i></div>';
    else
        return ''
}

function custom_button_cp(obj, common, value) {
    return '<div title="{{_("Duplicate element")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-copy"></i></div>'
}

function custom_button_rm(obj, common, value) {
    return '<div title="{{_("Remove element")|escapejs}}"><i style="cursor:pointer" class="webix_icon far fa-trash-alt"></i></div>'
}

function custom_button_detail(obj, common, value) {
    return '<div title="{{_("Detail")|escapejs}}"><i style="cursor:pointer" class="webix_icon fas fa-external-link-square-alt"></i></div>'
}

{# modal popup and image manage #}

function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}

function image_modal(url, width, height, id) {
    webix.ui({
        id: id,
        view: "window",
        height: height,
        width: width,
        head: {
            view: "toolbar", cols: [
                {view: "label", label: "{{_("Image")|escapejs}}"},
                {
                    view: "tootipButton",
                    label: '{{_("Close")|escapejs}}',
                    width: 100,
                    align: 'right',
                    click: "$$('" + id + "').close();"
                }
            ]
        },
        position: "center",
        body: {
            template: "<img src='" + url + "'>"
        }
    }).show();
}

function preloadImage(url) {
    var img = new Image();
    img.src = url + '?t=' + makeid();
}

{# loading and custom post simulation #}

function load_js(lnk, hide, area, method, data, headers, dataType, abortAllPending, done, fail, always) {
    if (abortAllPending == true) {
        $.xhrPoolAbortAll();
    }
    if (method == undefined) {
        method = 'GET'
    }
    if (data == undefined) {
        data = {}
    }
    if (data == headers) {
        data = {}
    }
    if ((area == undefined) || (area == '') || (area == null)) {
        area = '{{ webix_container_id }}';
    }
    hide = hide || 0;
    if (hide == true) {
        webix.ui([], $$(area));
    }
    if (dataType == 'json') {
        $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        $.ajax({
            url: lnk,
            dataType: "json",
            type: method,
            data: data,
        }).done(function (msg) {
            if (done != undefined) {
                return done(msg);
            } else {
                webix.ui.resize();
                $$(area).hideOverlay();
                return msg;
            }
        }).fail(function (xhr, textStatus) {
            if (fail != undefined) {
                return fail(xhr, textStatus);
            } else {
                webix.alert('{{_("Server error")|escapejs}}')
            }
        }).always(function (data, textStatus, errorThrown) {
            if (always != undefined) {
                always(data, textStatus, errorThrown);
            }
        })
    } else {
        if (lnk != '') {

            if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').showOverlay !== undefined)
                $$('{{ webix_overlay_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
            else if ($$(area) !== undefined && $$(area) !== null && $$(area).showOverlay !== undefined)
                $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");

            $.ajax({
                url: lnk,
                type: method,
                data: data,
                headers: headers,
                dataType: "script",
            }).done(function (msg) {
                if (done != undefined) {
                    return done(msg);
                } else {
                    if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                        $$('{{ webix_overlay_container_id }}').hideOverlay();
                    else if ($$(area) !== undefined && $$(area) !== null && $$(area).hideOverlay !== undefined)
                        $$(area).hideOverlay();
                    webix.ui.fullScreen();
                    window.dispatchEvent(new Event('resize'));
                }
            }).fail(function (xhr, textStatus) {
                if (fail != undefined) {
                    return fail(xhr, textStatus);
                } else {
                    if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                        $$('{{ webix_overlay_container_id }}').hideOverlay();
                    else if ($$(area) !== undefined && $$(area) !== null && $$(area).hideOverlay !== undefined)
                        $$(area).hideOverlay();
                    webix.alert('{{_("Server error")|escapejs}}')
                }
            }).always(function (data, textStatus, errorThrown) {
                if (always != undefined) {
                    always(data, textStatus, errorThrown);
                }
            });
        }
    }
}


function loading(url, blank, move_focus) {
    if (blank != undefined) {
        if (url != '') {
            window.open(url, '_blank');
        }
    } else {
        if (url != '') {
            document.location.href = url;
        }
    }
}

/**
 * sends a request to the specified url from a form. this will change the window location.
 * @param {string} path the path to send the post request to
 * @param {object} params the paramiters to add to the url
 */
function post(path, params) {

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    const form = document.createElement('form');
    form.method = 'post';
    form.action = path;

    const hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = 'csrfmiddlewaretoken';
    hiddenField.value = getCookie('csrftoken');
    form.appendChild(hiddenField);

    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}
{# autocomplete #}

function set_autocomplete_reload(selector, QS) {
    a = $$(selector);
    b = $$(a.config.suggest);
    c = b.getBody();
    c.define('dataFeed', QS);
    c.clearAll()
    c.refresh();
    d = a.getList();
    d.load(QS + '&filter[value]=');
}

function set_autocomplete_value(selector, QS, value) {
    a = $$(selector);
    b = $$(a.config.suggest);
    c = b.getBody();
    c.define('dataFeed', QS);
    c.refresh();
    d = a.getList();
    d.load(QS + '&filter[value]=' + value);
}

function set_autocomplete(selector, QS) {
    a = $$(selector);
    b = $$(a.config.suggest);
    c = b.getBody();
    c.define('dataFeed', QS);
    c.refresh();
    d = a.getList();
    d.load(QS + '&filter[value]=');
}

function set_autocomplete_empty(selector, QS) {
    a = $$(selector);
    d = a.getList();
    d.load(QS + '&filter[value]=');
}

{# webix extensions #}

webix.protoUI({
    name: "tootipButton",
    $cssName: "button",
    $init: function (obj) {
        if (obj.tooltip)
            this.$view.title = obj.tooltip;
    }
}, webix.ui.button)

webix.ui.datafilter.dataListCheckbox = webix.extend({
    refresh: function (master, node, config) {
        node.onclick = function () { // NOTA uncheck lo fa su tutto invece di solo quello che vede filtrato
            this.getElementsByTagName("input")[0].checked = config.checked = !config.checked;
            var column = master.getColumnConfig(config.columnId);
            var checked = config.checked ? column.checkValue : column.uncheckValue;

            var range = master.data.getIndexRange(master.data.$min, master.data.$max);
            for (var i = 0; i < range.length; i++) {
                var obj = range[i];
                obj[config.columnId] = checked;
                master.callEvent("onCheck", [obj.id, config.columnId, checked]);
            }
            master.refresh();
        };
    },
    render: function (master, config) {
        return "<input type='checkbox' " + (config.checked ? "checked='1'" : "") + "> {{_("All")|escapejs}}";
    }
}, webix.ui.datafilter.masterCheckbox);

webix.ui.datafilter.rowsCount = webix.extend({
    refresh: function (master, node, value) {
        node.firstChild.innerHTML = master.count();
    }
}, webix.ui.datafilter.summColumn)

webix.ui.datafilter.avgColumn = webix.extend({
    refresh: function (master, node, value) {
        var result = 0;
        master.mapCells(null, value.columnId, null, 1, function (value) {
            value = value * 1;
            if (!isNaN(value))
                result += value;
            return value;
        });

        node.firstChild.innerHTML = Math.round(result / master.count());
    }
}, webix.ui.datafilter.summColumn)
