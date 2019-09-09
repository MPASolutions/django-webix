{% load django_webix_utils %}

{% block webix_content %}

    {% block context_cleaner %}
        webix.ui([], $$("{{ webix_container_id }}"));
    {% endblock %}

    {% block toolbar_navigation %}
        $$("{{ webix_container_id }}").addView({
            id: 'main_toolbar_navigation',
            view: "toolbar",
            margin: 5,
            cols: [
                {
                    view: "template",
                    type: "header",
                    template: '<p style="text-align:center;">{% if object_list %}{{object_list.model|getattr:"_meta"|getattr:"verbose_name"}}{% endif %}</p>',
                }
            ]
        });
    {% endblock %}

    {% block objects_list %}
        var objects_list = [
          {% for obj in object_list_values %}
            {
              status: 0,
              {% for key, value in obj.items %}
                {{key}}: "{{ value|default_if_none:''|escapejs }}"{% if not forloop.last %}, {% endif %}
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
          columns: [
              {
                  id: "checkbox_action",
                  header: {content: "masterCheckbox", css: "center"},
                  template: "{common.checkbox()}",
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
                      load_js('{{ url_update }}'.replace('0', el.id));
                  }
              }
          }
      })
    {% endblock %}

    {% block toolbar_list %}
        var actions_list = undefined;
        var actions_execute = undefined;
        {% include "django_webix/include/toolbar_list.js" %}
    {% endblock %}

    {% block extrajs_post %}{% endblock %}

{% endblock %}
