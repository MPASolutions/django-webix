{% load static django_webix_utils i18n filtersmerger_utils %}

{% get_request_filter_params %}

String.prototype.toTitle = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

webix.editors.datetime = webix.extend( {
	focus	:function(){},
	popupType:"datetime",
	setValue:function(value){
		this._is_string = this.config.stringResult || (value && typeof value == "string");
		webix.editors.popup.setValue.call(this, value);
	},
	getValue:function(){
		return this.getInputNode().getValue(this._is_string?webix.i18n.parseFormatStr:"")||"";
	},
	popupInit:function(popup){
		popup.getChildViews()[0].attachEvent("onDateSelect", function(value){
			callEvent("onEditEnd",[value]);
		});
	}
}, webix.editors.popup);

webix.editors.$popup.datetime = {
    height: 250,
    width: 250,
    padding: 0,
    view: "popup",
    body: {
        view: "calendar", timepicker: true, icons: true, borderless: true
    },
}

webix.ui.datafilter.serverDateRangeFilter = webix.extend({
  getValue:function(t){
    var e=this.getInputNode(t);
    e.config.stringResult=true;
    //console.log(e.getValue());
    return e.getValue()
  }
}, webix.ui.datafilter.serverDateRangeFilter)

{# filters #}

if (webixAppliedFilters == undefined) {
    var webixAppliedFilters = {};
}

function setWebixFilter(app_model, filter_type, value){
    webixAppliedFilters[app_model][filter_type] = value;
}

function initWebixFilterPrefix(app_model){
    if (webixAppliedFilters[app_model] == undefined) {
        webixAppliedFilters[app_model] = {};
        {% for key, param in filter_params.items %}
        {% if param %}
         webixAppliedFilters[app_model]['{{ param }}'] = null;
        {% endif %}
        {%  endfor %}
    }
}

function resetWebixFilterPrefix(app_model){
    webixAppliedFilters[app_model] = {};
    {% for key, param in filter_params.items %}
    {% if param %}
    webixAppliedFilters[app_model]['{{ param }}'] = null;
    {% endif %}
    {%  endfor %}
    if('layer' in webixAppliedFilters[app_model]) {
        webixAppliedFilters[app_model]['layer'] = null;
    }
}

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

if (!String.prototype.startsWith) {
    Object.defineProperty(String.prototype, 'startsWith', {
        value: function (search, rawPos) {
            var pos = rawPos > 0 ? rawPos | 0 : 0;
            return this.substring(pos, pos + search.length) === search;
        }
    });
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
    avg: 'media',
    apply: "Applica",
    cancel: "Annulla",
    columns: "Colonne",
    count: "conteggio",
    fields: "Campi",
    filters: "Filtri",
    groupBy: "Raggruppa per",
    max: "max",
    min: "min",
    operationNotDefined: "Operazione non definita",
    pivotMessage: "Clicca per personalizzare",
    rows: "Righe",
    select: "selezione",
    sum: "somma",
    text: "testo",
    total: "Totale",
    values: "Valori",
    windowTitle: "Configurazione",
    windowMessage: "[Trascinare i campi di sinistra nella sezione desiderata]",
};

webix.i18n.locales['it-IT'].fullDateFormat = "%d/%m/%Y %H:%i:%s"

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

function custom_checkbox_yesnonone(obj, common, value) {
    if ((value === "True") || (value === "true") || (value == '1') || (value === 1) || (value === true)) {
        return "<div style='color:green;'>{{_("Yes")|escapejs}}</div>";
    } else if ((value === "False") || (value === "false") || (value == '0') || (value === 0) || (value === false)) {
        return "<div style='color:red;'>{{_("No")|escapejs}}</div>";
    } else {
        return "";
    }
}

function template_colour_rgb(obj, common, value) {
    return '<div style="border:1px solid #000;height:15px;background-color: '+value+'"></div>';
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

/**
 * Helper to send request (ajax or http redirect)
 *
 * @param lnk url of the new request
 * @param hide specify if hide loading area
 * @param area location to add loader
 * @param method http method [GET, POST, etc.]
 * @param data data to send to request
 * @param headers header to send to request
 * @param dataType type of expected response
 * @param abortAllPending if ajax and true, then abort pending requests
 * @param done function to call at the end of request (success)
 * @param fail function to call when request fails (error)
 * @param always function to call in any case
 * @param ajaxExtra extra dict to merge with ajax params
 */
function load_js(lnk, hide, area, method, data, headers, dataType, abortAllPending, done, fail, always, ajaxExtra, enableHistory) {
    asyncRequest = typeof asyncRequest !== 'undefined' ? asyncRequest : true;
    method = typeof method !== 'undefined' ? method : 'GET';
    data = typeof data !== 'undefined' ? data : {};
    dataType = typeof dataType !== 'undefined' ? dataType : 'script';
    hide = typeof hide !== 'undefined' ? hide : false;
    ajaxExtra = typeof ajaxExtra !== 'undefined' ? ajaxExtra : {};
    enableHistory = typeof enableHistory !== 'undefined' ? enableHistory : true;

    if (abortAllPending == true) {
        $.xhrPoolAbortAll();
    }
    if (data == headers) {
        data = {};
    }
    if (area === undefined || area === '' || area === null) {
        area = '{{ webix_container_id }}';
    }
    if (hide === true) {
        webix.ui([], $$(area));
    }

    if (dataType == 'json') {
        $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
        $.ajax($.extend({
            url: lnk,
            dataType: "json",
            type: method,
            data: data,
        }, ajaxExtra)).done(function (msg) {
            if (typeof done === 'function') {
                return done(msg);
            } else {
                webix.ui.resize();
                $$(area).hideOverlay();
                return msg;
            }
        }).fail(function (xhr, textStatus) {
            if (typeof fail === 'function') {
                return fail(xhr, textStatus);
            } else {
                    if (textStatus!='abort') {
                        webix.alert('{{_("Server error")|escapejs}}')
                    }
            }
        }).always(function (data, textStatus, errorThrown) {
            if (typeof always === 'function') {
                always(data, textStatus, errorThrown);
            }
        })
    } else {
        if (lnk != '') {

            if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').showOverlay !== undefined)
                $$('{{ webix_overlay_container_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
            else if ($$(area) !== undefined && $$(area) !== null && $$(area).showOverlay !== undefined)
                $$(area).showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");

            $.ajax($.extend({
                url: lnk,
                type: method,
                data: data,
                headers: headers,
                dataType: dataType,
            }, ajaxExtra)).done(function (msg) {
                if (typeof done === 'function') {
                    return done(msg);
                } else {
                    if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                        $$('{{ webix_overlay_container_id }}').hideOverlay();
                    else if ($$(area) !== undefined && $$(area) !== null && $$(area).hideOverlay !== undefined)
                        $$(area).hideOverlay();
                    webix.ui.fullScreen();
                    if (navigator.userAgent.indexOf('MSIE') !== -1 || navigator.appVersion.indexOf('Trident/') > 0) {
                        var evt = document.createEvent('UIEvents');
                        evt.initUIEvent('resize', true, false, window, 0);
                        window.dispatchEvent(evt);
                    } else {
                        window.dispatchEvent(new Event('resize'));
                    }
                    // change state
                    {% if history_enable %}
                    if (enableHistory == true) {
                        extra_url = '?state=' + lnk;
                        if ($$('main_content_right') != undefined) {
                            extra_url += '&tab=' + $$('main_content_right').getValue();
                        }
                        history.replaceState(null, null, extra_url);
                    }
                    {% endif %}
                }
            }).fail(function (xhr, textStatus) {
                if (typeof fail === 'function') {
                    return fail(xhr, textStatus);
                } else {
                    if ($$('{{ webix_overlay_container_id }}') !== undefined && $$('{{ webix_overlay_container_id }}') !== null && $$('{{ webix_overlay_container_id }}').hideOverlay !== undefined)
                        $$('{{ webix_overlay_container_id }}').hideOverlay();
                    else if ($$(area) !== undefined && $$(area) !== null && $$(area).hideOverlay !== undefined)
                        $$(area).hideOverlay();
                    if (textStatus!='abort') {
                        webix.alert('{{_("Server error")|escapejs}}')
                    }
                }
            }).always(function (data, textStatus, errorThrown) {
                if (typeof always === 'function') {
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
function webix_post(path, params) {

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement('form');
    form.method = 'post';
    form.action = path;

    var hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = 'csrfmiddlewaretoken';
    hiddenField.value = getCookie('csrftoken');
    form.appendChild(hiddenField);

    for (var key in params) {
        if (params.hasOwnProperty(key)) {
            var hiddenField = document.createElement('input');
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

function set_autocomplete_reload(selector, QS, finally_function) {
    var a = $$(selector);
    var d = a.getList();
    if(a.config.view === 'multicombo' || a.config.view === 'multiselect'){
        if(d.config.dataFeed == undefined) {
            d.define('dataFeed', QS);
        }else{
            d.config.dataFeed = QS
        }
        d.clearAll();
    } else {
        var b = $$(a.config.suggest);
        var c = b.getBody();
        if(c.config.dataFeed == undefined) {
            c.define('dataFeed', QS);
        }else{
            c.config.dataFeed = QS
        }
        c.clearAll();
        c.refresh();
    }
    if (finally_function==undefined){
        finally_function=function(){}
    }
    d.load(QS + '&filter[value]=').finally(finally_function);
    d.refresh();
}

function set_autocomplete_value(selector, QS, value, finally_function) {
    var a = $$(selector);
    var d = a.getList();
    if(a.config.view === 'multicombo' || a.config.view === 'multiselect'){
        if(d.config.dataFeed == undefined) {
            d.define('dataFeed', QS);
        }else{
            d.config.dataFeed = QS
        }
        d.clearAll();
    }else {
        var b = $$(a.config.suggest);
        var c = b.getBody();
        if(c.config.dataFeed == undefined) {
            c.define('dataFeed', QS);
        }else{
            c.config.dataFeed = QS
        }
        c.refresh();
    }
    d.load(QS + '&filter[value]=' + value).finally(finally_function);
    d.refresh();
}

function set_autocomplete(selector, QS, finally_function) {
    var a = $$(selector);
    var d = a.getList();
    if(a.config.view === 'multicombo' || a.config.view === 'multiselect'){
        d.define('dataFeed', QS);
        d.clearAll();
    }else {
        var b = $$(a.config.suggest);
        var c = b.getBody();
        if(c.config.dataFeed == undefined) {
            c.define('dataFeed', QS);
        }else{
            c.config.dataFeed = QS
        }
        c.refresh();
    }
    d.load(QS + '&filter[value]=').finally(finally_function);
    d.refresh();
}

function set_autocomplete_empty(selector, QS, finally_function) {
    var a = $$(selector);
    var d = a.getList();
    d.load(QS + '&filter[value]=').finally(finally_function);
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

function sortFloat(a, b) {
    a = parseFloat(a.data6);
    b = parseFloat(b.data6);
    return a > b ? 1 : (a < b ? -1 : 0);
}

function floateditor(obj, common, value, config) {
    var anno = config.id.replace('menu_','');
    var lock = obj[config.id+'_lock'];
    if (lock!=true) {
        var floaticon = "<div title='{{_("Click and change")|escapejs}}'> " + value + "&nbsp;&nbsp;&nbsp;<span style='float:right;margin-top:3px;text-align:right;' class='webix_icon far fa-edit'></span></div>";
    } else {
        var floaticon = "<div title='{{_("Locked data")|escapejs}}'> " + value + "</div>";
    }
    return floaticon;
}

function filter_icontains(item, value) {
    if (item.value.toString().toLowerCase().indexOf(value.toLowerCase()) >= 0)
        return true;
    return false;
}

function update_geo_ewkt_point(geo_field_selector){
    //'SRID=32632;POINT (663156.5901635507 5099188.654177771)'
    if ( ($$(selector + '_long')!='') && ($$(selector + '_lat')!='') && ($$(selector + '_srid')!='') ) {
        $$(selector).setValue('SRID='+$$(selector + '_srid').getValue()+';POINT ('+$$(selector + '_long').getValue()+' '+$$(selector + '_lat').getValue()+')');
    }
}

function i18nNumberFormat(decimalSize) {
    return webix.Number.numToStr({
        groupDelimiter: webix.i18n.groupDelimiter,
        groupSize: webix.i18n.groupSize,
        decimalDelimiter: webix.i18n.decimalDelimiter,
        decimalSize: decimalSize
    })
}

function geo_change(geo_type, field_name){
    /*
    str = 'Content(cap)(cap2)(cap3)'
    str.match(/(\(.*?\))/g)
    var i = $(this).attr("id").match(/(?:-\d+)?(-\d+-)/);
    //'SRID=32632;POINT (663156.5901635507 5099188.654177771)'
    var str = $$(geo_field_selector).getValue()
    let pattern = /SRID=(?P<srid>-?\d+);POINT \((?P<longitude>-?\d+\.\d+) (?P<latitude>-?\d+\.\d+)\)/g
    str.match(pattern);
    let arr = patter.exec( str );
  return arr[1];
     */
}
