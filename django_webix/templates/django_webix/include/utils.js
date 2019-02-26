{% load static %}

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

function load_pdf(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

function custom_checkbox(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == false))
        return "<img style='width:12px;' src='{% static 'admin/img/icon-no.svg' %}'> "
    else
        return "<img style='width:12px;' src='{% static 'admin/img/icon-yes.svg' %}'> "
}

function custom_checkbox_pointer(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == false))
        return "<img style='width:12px;cursor:pointer' src='{% static 'admin/img/icon-no.svg' %}'> "
    else
        return "<img style='width:12px;cursor:pointer' src='{% static 'admin/img/icon-yes.svg' %}'> "
}

function custom_checkbox_help(obj, common, value) {
    if ((value == 'False') || (value == 'false') || (value == false))
        return "<img style='width:12px;cursor:help' src='{% static 'admin/img/icon-no.svg' %}'> "
    else
        return "<img style='width:12px;cursor:help' src='{% static 'admin/img/icon-yes.svg' %}'> "
}

function custom_checkbox_yesno(obj, common, value) {
    if (value)
        return "<div style='color:green;'>Sì</div>";
    else
        return "<div style='color:red;'>No</div>";
}

function custom_button_cp() {
    return '<div title="Duplica elemento"><i style="cursor:pointer" class="webix_icon fa-copy"></i></div>'
}

function custom_button_rm() {
    return '<div title="Rimuovi elemento"><i style="cursor:pointer" class="webix_icon fa-trash-o"></i></div>'
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
                {view: "button", label: 'Chiudi', width: 100, align: 'right', click: "$$('" + id + "').close();"}
            ]
        },
        position: "center",
        body: {
            template: "<img src='" + url + "'>"
        }
    }).show();
}

function load_js(lnk, hide, area) {
    if ((area == undefined) || (area == '') || (area == null)) {
        area = 'content_right';
    }
    if (lnk != '') {
        hide = hide || 0;
        if (hide == true) {
            webix.ui([], $$(area));
        }
        $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        $.ajax({
            url: lnk,
            dataType: "script",
            success: function () {
                //    setTimeout(function(){
                $$(area).hideOverlay();
                webix.ui.fullScreen();
                window.dispatchEvent(new Event('resize'));
//        },2000); // monkey patch
            },
            error: function () {
                alert('si è verificato un errore')
            }
        });
    }
}

function load_js_data(lnk, area) {
    if ((area == undefined) || (area == '') || (area == null)) {
        area = 'content_right';
    }
    $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
    $.ajax({
        url: lnk,
        dataType: "json",
        success: function (msg) {
            webix.ui.resize();
            $$(area).hideOverlay();
            return msg;
        },
        error: function () {
            alert('si è verificato un errore')
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

