{% load django_webix_utils %}

{% block webix_content %}

    {% block context_cleaner %}
        webix.ui([], $$("{{ webix_container_id }}"));
    {% endblock %}

    {% block toolbar_navigation %}
        {% if title %}
            $$("{{ webix_container_id }}").addView({
                id: 'main_toolbar_navigation',
                view: "toolbar",
                margin: 5,
                cols: [
                    {
                        view: "template",
                        type: "header",
                        template: '<div style="width:100%; text-align:center;"><strong>{{ title }}</strong></div>',
                    }
                ]
            });
        {% endif %}
    {% endblock %}

    {% block objects_list %}
        var objects_list = [

          {% for obj in objects_datatable %}
            {
              status: 0,
              {% for key, value in obj.items %}
                {{key}}: "{{ value|format_list_value|escapejs }}"{% if not forloop.last %}, {% endif %}
              {% endfor %}
              {% block extra_columns %}{% endblock %}
            }{% if not forloop.last %}, {% endif %}
          {% endfor %}
        ]
    {% endblock %}

    {% block datatable %}
      $$("{{ webix_container_id }}").addView({
          id: 'datatable_{{model_name}}',
          view: "datatable",
          leftSplit: 1,
          select:   "row",
          resizeColumn: true,
          {% block datatable_headermenu %}
              headermenu: {
                  width: 250,
              },
          {% endblock %}
          columns: [
              {
                  id: "checkbox_action",
                  header: [{content: "headerMenu"},{content: "masterCheckbox", css: "center"}],
                  template: "{common.checkbox()}",
                  tooltip:false,
                  headermenu:false,
                  width: 40,
                  minWidth: 40,
                  maxWidth: 40,
                  css: {'text-align': 'right'}
              },
              {% block datatable_columns %}
                {% for field in fields %}
                    {{ field.datalist_column|safe }},
                {% endfor %}
              {% endblock %}
              {% block datatable_columns_commands %}
              {% if has_add_permission %}
              {% if is_enable_column_copy %}
              {
                  id: "cmd_cp",
                  header: "",
                  adjust: "data",
                  headermenu:false,
                  tooltip:false,
                  template: custom_button_cp,
              },
              {% endif %}
              {% endif %}
              {% if has_delete_permission %}
              {% if is_enable_column_delete %}
              {
                  id: "cmd_rm",
                  header: "",
                  adjust: "data",
                  headermenu:false,
                  tooltip:false,
                  template: custom_button_rm,
              }
              {% endif %}
              {% endif %}
              {% endblock %}
          ],
          data: objects_list,
          navigation: true,
          //footer: true,
          checkboxRefresh: true,
          headermenu: {width: 200},
          on: {
              onItemClick: function (id, e, trg) {
                  var el = $$('datatable_{{model_name}}').getSelectedItem();
                  if (id.column == 'cmd_cp') {
                      load_js('{{ url_create }}?pk_copy=' + el.id);
                  } else if (id.column == 'cmd_rm') {
                      load_js('{{ url_delete }}'.replace('0', el.id));
                  } else {
                      {% if is_enable_row_click %}
                      load_js('{{ url_update }}'.replace('0', el.id));
                      {% endif %}
                  }
              }
          }
      })
    {% endblock %}

    {% block toolbar_list %}
        {% block toolbar_list_actions %}
            var actions_list = [
                  {id: "excel_standard", value: "EXCEL: Esporta dati"},
                  ];
            function actions_execute(action, ids) {
              if (action == "excel_standard") {
                   webix.toExcel(
                       $$("datatable_{{model_name}}"),
                       {
                           filter:function(obj) {
                               return obj.checkbox_action;
                           },
                           filename:"Dati",
                           name:"Dati",
                           filterHTML:true,
                           ignore: {"checkbox_action": true, "cmd_rm": true, "cmd_cp": true}
                       }
                       );
                }
            }
        {% endblock %}
        {% include "django_webix/include/toolbar_list.js" %}
    {% endblock %}

    {% block extrajs_post %}{% endblock %}

{% endblock %}
