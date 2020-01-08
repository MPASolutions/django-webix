{% load static django_webix_utils %}

// csrf set
// using jQuery
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

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            var csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Italian locale settings for pivot
webix.i18n.pivot = {
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


function load_pdf(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

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
        return "<div style='color:green;'>Sì</div>";
    else
        return "<div style='color:red;'>No</div>";
}

function custom_checkbox_default(obj, common, value) {
    if (value)
        return '<div title="Default"><i style="cursor:pointer" class="webix_icon fas fa-check-circle"></i></div>';
    else
        return ''
}

function custom_button_geo(obj, common, value) {
    if (value)
        return '<div title="Vedi in mappa"><i style="cursor:pointer" class="webix_icon fas fa-map-marker-alt"></i></div>';
    else
        return ''
}

function custom_button_cp(obj, common, value) {
    return '<div title="Duplica elemento"><i style="cursor:pointer" class="webix_icon far fa-copy"></i></div>'
}

function custom_button_rm(obj, common, value) {
    return '<div title="Rimuovi elemento"><i style="cursor:pointer" class="webix_icon far fa-trash-alt"></i></div>'
}

function custom_button_detail(obj, common, value) {
    return '<div title="Dettaglio elemento"><i style="cursor:pointer" class="webix_icon fas fa-external-link-square-alt"></i></div>'
}

function image_modal(url, width, height, id) {
    webix.ui({
        id: id,
        view: "window",
        height: height,
        width: width,
        head: {
            view: "toolbar", cols: [
                {view: "label", label: "Immagine"},
                {view: "tootipButton", label: 'Chiudi', width: 100, align: 'right', click: "$$('" + id + "').close();"}
            ]
        },
        position: "center",
        body: {
            template: "<img src='" + url + "'>"
        }
    }).show();
}

function load_js(lnk, hide, area, method, data) {
    if (method == undefined) {
        method = 'GET'
    }
    if (data == undefined) {
        data = {}
    }
    if ((area == undefined) || (area == '') || (area == null)) {
        area = '{{ webix_container_id }}';
    }
    if (lnk != '') {
        hide = hide || 0;
        if (hide == true) {
            webix.ui([], $$(area));
        }
        $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        $.ajax({
            url: lnk,
            type: method,
            data: data,
            dataType: "script",
            success: function () {
                //    setTimeout(function(){
                $$(area).hideOverlay();
                webix.ui.fullScreen();
                window.dispatchEvent(new Event('resize'));
//        },2000); // monkey patch
            },
            error: function () {
                webix.alert('Server error')
            }
        });
    }
}

function load_js_data(lnk, area, method, data) {
    if (method == undefined) {
        method = 'GET'
    }
    if (data == undefined) {
        data = {}
    }
    if ((area == undefined) || (area == '') || (area == null)) {
        area = '{{ webix_container_id }}';
    }
    $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
    $.ajax({
        url: lnk,
        dataType: "json",
        type: method,
        data: data,
        success: function (msg) {
            webix.ui.resize();
            $$(area).hideOverlay();
            return msg;
        },
        error: function () {
            webix.alert('Server error')
        }
    });
}

function loading_blank(url) {
    if (url != '') {
        window.open(url, '_blank');
    }
}

function loading(url) {
    if (url != '') {
        document.location.href = url;
    }
}

function preloadImage(url) {
    var img = new Image();
    img.src = url + '?t=' + makeid();
}

function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}


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
        return "<input type='checkbox' " + (config.checked ? "checked='1'" : "") + "> Tutti";
    }
}, webix.ui.datafilter.masterCheckbox);

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
