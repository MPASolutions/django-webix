{% load django_webix_utils i18n %}

{% block webix_warnings %}
var warnings = [
    {%  for warning in warnings %} {'label':'{{ warning.0|escapejs }}', 'message':'{{ warning.1|escapejs }}'} {% endfor %}
    ]

function show_warnings(warnings) {
    if (warnings.length > 0) {
        webix.ui({
            view: "window",
            id: "popup_form_warnings_win",
            width: 600,
            height: 400,
            scrool: 'y',
            position: "center",
            modal: true,
            head: {
                view: "toolbar", cols: [
                    {view: "label", label: '{{_("Oops! Some warnings here...")|escapejs}}'},
                    {
                        view: "button",
                        label: '{{_("Close")|escapejs}}',
                        width: 100,
                        align: 'right',
                        click: "$$('popup_form_warnings_win').destructor();"
                    }
                ]
            },
            body: {
                rows: [
                    {
                        id: "warnings_list",
                        view: "list",
                        type: {height: "auto"},
                        template: function (item) {
                            if (item.label == null)
                                return "<b>" + item.warning + "</b></p>";
                            else
                                return "<p style='margin:5px 0px;'><b>" + item.label + "</b>: " + item.message + "</p>";
                        },
                        data: warnings
                    },
                    {
                        id: 'warnings_toolbar',
                        view: "toolbar",
                        margin: 5,
                        cols: [
                             {
                                  view: "button",
                                  id: "warnings_cancel",
                                  label: '{{_("Undo")|escapejs}}',
                                  width: 100,
                                  align: 'left',
                                  click: function () {
                                      $$('popup_form_warnings_win').destructor();
                                  }
                              },
                              {},
                              {
                                  view: "button",
                                  id: "warnings_ok",
                                  label: '{{_("Continue anyway")|escapejs}}',
                                  width: 200,
                                  align: 'right',
                                  click: function () {
                                      webix.storage.local.put("{{ form.webix_id }}_warnings_accepted", true);
                                      id = webix.storage.local.get("last_button_click");
                                      if ($$(id)!=undefined) {
                                          $$('popup_form_warnings_win').destructor();
                                          webix.html.triggerEvent($$(id).getInputNode(), "MouseEvents", "click");
                                      }
                                  }
                              }
                        ]
                    }
                ]
            }
        }).show();
    }
}
show_warnings(warnings);

{% block extrajs_post %}{% endblock %}
{% endblock %}
