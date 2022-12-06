{% extends "django_webix/generic/list.js" %}
{% load static i18n %}

{% block webix_content %}
    {% get_media_prefix as media_prefix %}

    function download_attachment(pk, pdf_view) {
      webix.ajax().get("{% url 'dwsender.attachment_check' %}" + '?pk_attachment=' + pk, {
        success: function (text, data, XmlHttpRequest) {
          var result = data.json();
          if ('exist' in result && result.exist) {
            var file_path = '{{ media_prefix }}' + result.path;
            if (pdf_view &&'is_pdf' in result && result.is_pdf){
                webix.ui({
                  view:"window",
                  id:"pdfviewer_window",
                  modal:true,
                  move:true,
                  resize: true,
                  position:function(state){
                    state.top = 0;
                    state.left = 50;
                    state.width = state.maxWidth - 100;
                    state.height = state.maxHeight - 50;
                  },
                  head:{
                    view:"toolbar", cols:[
                      {},
                      { view:"button", label: 'Chiudi', width: 100, align: 'left', click:function(){ $$('pdfviewer_window').close(); }}
                    ]
                  },
                  body:{
                    rows:[
                    { view:"pdfbar", id:"pdfviewer_toolbar" },
                    {
                      view:"pdfviewer",
                      id:"pdfviewer_view",
                      toolbar:"pdfviewer_toolbar",
                      url:"binary->" + file_path,
                      downloadName: result.name
                    }
                  ]
                  }
                }).show();
            } else {
                var a = document.createElement('A');
                a.href = file_path;
                a.download = file_path.substr(file_path.lastIndexOf('/') + 1);
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
          }else {
            webix.alert({
              title: "{{ _("File mancante")|escapejs }}",
              ok: "{{ _("Ok")|escapejs }}",
              text: "{{ _("File ancora non presente.")|escapejs }}",
            });
          }
        },
        error: function (text, data, XmlHttpRequest) {
          webix.alert({
            title: "{{ _("File mancante")|escapejs }}",
            ok: "{{ _("Ok")|escapejs }}",
            text: "{{ _("File ancora non presente.")|escapejs }}",
          });
        },
      });
    }

    var attachmentsTemplate = function (obj, common, value, config) {
        var values = String(value).split('|').filter(Boolean);
        var result = "";
        for (var index = 0; index < values.length; ++index) {
            result += "<span style='text-decoration: none; color: black; padding-right: 5px;' > <i onclick='download_attachment(\"" + values[index] + "\", true)' class='far fa-file-alt'></i> </span>";
            result += "<span style='text-decoration: none; color: black; padding-right: 5px;' > <i onclick='download_attachment(\"" + values[index] + "\", false)' class='far fa-arrow-to-bottom'></i> </span><br>";
        }
        return result;
    };

    {{ block.super }}

    $$('{{ view_prefix }}datatable').attachEvent("onAfterLoad", function () {
        this.adjustRowHeight();
        this.render();
    });
{% endblock %}

{% block datatable_headermenu %}
    fixedRowHeight: false,
    rowLineHeight: 25,
    rowHeight: 25,
{% endblock %}
