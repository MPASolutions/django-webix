{% load i18n %}

{% if importer and not importer.valid %}
webix.ui({
  id: 'err_pop',
  view: "window",
  width: 700, height: 700,
  modal: true,
  move: true,
  resize: true,
  css: ".webix_alert-error",
  position: "center",
  head: {
    rows: [
      {
        view: "toolbar",
        cols: [
          {
            view: "label",
            css: {'font-weight': 'bold'},
            label: "{{_('Attachment')|escapejs}}: &nbsp; {% if importer.nerrors > 0 %} {{ importer.nerrors }}{% else %} 0 {% endif %}  {% if importer.nerrors > 1 %}{{_('errors')|escapejs }}{% else %}{{ _('error')|escapejs}}{% endif %}" +
              " &nbsp; {{_('and')|escapejs }} &nbsp; {% if importer.nwarnings > 0 %} {{ importer.nwarnings }}{% else %} 0 {% endif %} {% if importer.nwarnings > 1 %} warnings {% else %} warning {% endif %}"
          }, //5c5c5c background
          /*{
            view: "button",
            type: 'iconButton',
            width: 27,
            icon: 'fas fa-times',
            align: 'right',
            click: "$$('err_pop').close();"
          },*/
        ]
      },
      {
        view: "label",
        css: {"background": "#8B0000 !important", 'color': '#ccc !important', 'font-weight': 'bold'},
        label: "&nbsp;&nbsp;{{ importer.meta.filename }} ({{_("sheet")|escapejs}} {{ importer.meta.sheet }})"
      },
    ],
  },
  body: {
    rows: [
      {% if importer.nerrors > 0 %}
      {
        view: "toolbar",
        // css: "highlighted_header header2",
        paddingX: 5,
        paddingY: 5,
        height: 40,
        cols: [
          {
            "template": "<span class='webix_icon fas fa-exclamation-circle'></span><b> {{_("Errors")|escapejs}} </b>",
            "css": "sub_title2",
            borderless: true
          }
        ]
      },
      {
        view: "unitlist",
        id: "list",
        select: true,
        padding: 40,
        scheme: {
          $sort: {
            by: "title",
            dir: 'asc'
          }
        },
        //uniteBy: '#pos#^ riga',
        uniteBy: function (obj) {
          //check if pos is not valid integer
          if (isNaN(parseInt(obj.pos))) { // now only obj.pos==='GENERALE'
            return obj.pos;
          } else {
            return obj.pos + '^ {{_("row")|escapejs}}';
          }
        },
        //template: "<b>#field#:</b> #mess#",
        template: function (obj) {
          if (isNaN(parseInt(obj.pos))) { // now only obj.pos==='GENERALE'
            return '<b>' + obj.field + '</b>: ' + obj.mess;
          } else if (obj.field === 'OTHER') {
            return '<b>{{_("Global controls")|escapejs}}</b>: ' + obj.mess;
          } else if (obj.value) {
            return '{{_("Column")|escapejs}} <b>' + obj.field + '</b> [' + obj.value + ']: ' + obj.mess;
          } else {
            return '{{_("Column")|escapejs}} <b>' + obj.field + '</b>: ' + obj.mess;
          }
        },
        type: {
          height: "auto"
        },
        data: [
          {% for el in importer.errors %}
          {
            pos: '{{ el.pos|escapejs }}',
            field: '{{ el.field|escapejs }}',
            value: '{{ el.value|escapejs }}',
            mess: '{{ el.mess|escapejs }}'
          },
          {% endfor %}
        ]
      },
      {% endif %}

      {% if importer.nwarnings > 0 %}
      {
        view: "toolbar",
        // css: "highlighted_header header2",
        paddingX: 5,
        paddingY: 5,
        height: 40,
        cols: [
          {
            "template": "<span class='webix_icon fas fa-exclamation'></span><b> {{_("Warnings")|escapejs}} </b>",
            "css": "sub_title2",
            borderless: true
          }
        ]
      },
      {
        view: "unitlist",
        id: "list",
        select: true,
        padding: 40,
        scheme: {
          $sort: {
            by: "title",
            dir: 'asc'
          }
        },
        //uniteBy: '#pos#^ riga',
        uniteBy: function (obj) {
          //check if pos is not valid integer
          if (isNaN(parseInt(obj.pos))) { // now only obj.pos==='GENERALE'
            return obj.pos;
          } else {
            return obj.pos + '^ {{_("row")|escapejs}}';
          }
        },
        //template: "<b>#field#:</b> #mess#",
        template: function (obj) {
          if (isNaN(parseInt(obj.pos))) { // now only obj.pos==='GENERALE'
            return '<b>' + obj.field + '</b>: ' + obj.mess;
          } else if (obj.field === 'OTHER') {
            return '<b>{{_("Global controls")|escapejs}}</b>: ' + obj.mess;
          } else if (obj.value) {
            return '{{_("Column")|escapejs}} <b>' + obj.field + '</b> [' + obj.value + ']: ' + obj.mess;
          } else {
            return '{{_("Column")|escapejs}} <b>' + obj.field + '</b>: ' + obj.mess;
          }
        },
        type: {
          height: "auto"
        },
        data: [
          {% for el in importer.warnings %}
          {
            pos: '{{ el.pos|escapejs }}',
            field: '{{ el.field|escapejs }}',
            value: '{{ el.value|escapejs }}',
            mess: '{{ el.mess|escapejs }}'
          },
          {% endfor %}
        ]
      },
      {% endif %}

      {
        view: "toolbar",
        margin: 5,
        id: "toolbar_confirm_validation",
        cols: [
          {
            view: "button",
            align: "left",
            icon: "eraser",
            id: 'close',
            label: "{{_("Close and correct")|escapejs}}",
            on: {
              'onItemClick': function (id) {
                $$('err_pop').close();
              }
            }
          },
          {},
          /*
          {% if importer.nwarnings > 0 and  importer.nerrors == 0%}
          {
            view: "button",
            align: "left",
            icon: "eraser",
            id: 'continue',
            label: "{{_("Continue with warnings")|escapejs}}",
          }
          {% else %}
          {},
          {% endif %}
          */
        ]
      }
    ]
  }
}).show();
{% endif %}
