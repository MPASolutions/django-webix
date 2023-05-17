{% load django_webix_utils static i18n %}

{% if is_enable_actions %}

var {{ view_prefix }}actions_list = [
    {% block actions_list %}
    {% for layer in layers %}
        {id: 'gotowebgis_{{ layer.codename }}', value: "{{_("Go to map")|escapejs}} ({{layer.layername}})"},
        {id: 'filtertowebgis_{{ layer.codename }}', value: "{{_("Filter in map")|escapejs}} ({{layer.layername}})"},
    {% endfor %}
    {% for action_key,action in actions.items %}
    {id: '{{ action_key }}', value: '{{action.short_description}}'},
    {% endfor %}
    {% endblock %}
];

{% for action_key,action in actions.items %}
{% if action.dynamic %}
      function _{{ action_key }}_action_execute_dynamic(ids, all) {
          $$('{{ view_prefix }}datatable').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
          var _params = $.extend({}, webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']);
          _params['action'] = '{{ action_key }}';
          _params['csrfmiddlewaretoken'] = getCookie('csrftoken');
          _params['dynamic'] = true;
          _params['all'] = all;
          if (all === false) {
              _params['ids'] = ids.join(',');
          }
          $.ajax({
              url: "{{ url_list|safe }}",
              type: "POST",
              dataType: 'script', // directly execute
              data: _params,
              error: function (jqXHR, textStatus, errorThrown) {
                  webix.message({
                      text: "{{ _("Action is not executable")|escapejs }}",
                      type: "error",
                      expire: 10000
                  });
                  $$('{{ view_prefix }}datatable').hideOverlay();
              },
              success: function (data) {
                  $$('{{ view_prefix }}datatable').hideOverlay();

              }
          });
      }
{% else %}
    {% if action.form %}
function _{{ action_key }}_action_execute_form(ids, all) {
  {% block action_execute_form %}
  webix.ui({
    view: "window",
    id: "{{ action_key }}_win",
    width: 550,
    maxHeigth: 600,
    scrool: 'y',
    position: "center",
    modal: true,
    move:true,
    resize: true,
    head: {
      view: "toolbar", cols: [
        {view: "label", label: '{{action.modal_header|escapejs}}'},
        {view: "button", label: '{{_("Close")|escapejs}}', width: 100, align: 'right', click: "$$('{{ action_key }}_win').destructor();"}
      ]
    },
    body: {
        view: 'form',
        id: '{{ action.form.webix_id }}',
        name: '{{ action.form.webix_id }}',
        borderless: true,
        elements: [
            {{ action.form.as_webix|safe }},
            {
                id: '{{ action_key }}_toolbar_form',
                view: "toolbar",
                margin: 5,
                cols: [
                    {$template: "Spacer"},
                    {
                        id: '{{ action.form.webix_id }}_set',
                        view: "tootipButton",
                        type: "form",
                        align: "right",
                        label: "{{action.modal_click|escapejs}}",
                        click: function () {
                            if ($$('{{ action.form.webix_id }}').validate({hidden:true, disabled:true})) {
                                webix.extend($$('{{ action.form.webix_id }}'), webix.OverlayBox);
                                $$('{{ action.form.webix_id }}').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
                                _{{ view_prefix }}action_execute(
                                                '{{ action_key }}',
                                                ids,
                                                all,
                                                '{{ action.response_type }}',
                                                '{{ action.short_description }}',
                                                '{{ action.modal_title }}',
                                                '{{ action.modal_ok }}',
                                                '{{ action.modal_cancel }}',
                                                $$('{{ action.form.webix_id }}').getValues(),
                                                function() {$$('{{ action.form.webix_id }}').hideOverlay(); $$('{{ action_key }}_win').destructor()},
                                                function() {$$('{{ action.form.webix_id }}').hideOverlay();},
                                                {% if action.reload_list %}true{% else %}false{% endif %}
                                        )
                            }
                        }
                    },
                    {$template: "Spacer"}
                ]
            }
        ],
        rules: {
            {% for field_name, rules in action.form.get_rules.items %}
            '{{ field_name }}': function (value) {
                return {% for r in rules %}{{r.rule}}('{{ field_name }}', value{% if r.max %},{{ r.max }}{% endif %}{% if r.min %}, {{ r.min }}{%endif %}){% if not forloop.last %} &&
                {% endif %}{% endfor %}
            },
            {% endfor %}
        },
    }
  }).show();
  {% endblock %}
}
    {% endif %}

    {% if action.template_view %}
      function _{{ action_key }}_action_execute_template_view(ids, all) {
          var templateViewWindow = webix.ui({
              view: "window",
              id: "{{ action_key }}_win",
              width: 550,
              maxHeigth: 600,
              scrool: 'y',
              position: "center",
              modal: true,
              move: true,
              resize: true,
              head: {
                  view: "toolbar", cols: [
                      {view: "label", label: '{{ action.short_description|escapejs }}'},
                  ]
              },
              body: {
                  rows: [
                      {
                          id: "{{ action_key }}_win_body",
                          rows: []
                      },
                      {
                          view: "toolbar",
                          id: "{{ action_key }}_footer",
                          cols: [
                              {
                                  view: "button",
                                  id: "{{ action_key }}_modal_cancel",
                                  label: '{{ action.modal_cancel }}',
                                  width: 100,
                                  align: 'right',
                                  click: function () {
                                      $$('{{ action_key }}_win').destructor();
                                  }
                              },
                              {},
                              {
                                  view: "button",
                                  id: "{{ action_key }}_modal_ok",
                                  label: '{{ action.modal_ok }}',
                                  width: 100,
                                  align: 'right',
                                  click: function () {
                                      $$('{{ action_key }}_win').destructor();
                                      {% if action.form %}
                                        _{{ action_key }}_action_execute_form(ids, all);
                                      {% else %}
                                          _{{ view_prefix }}action_execute(
                                              '{{ action_key }}',
                                              ids,
                                              all,
                                              '{{ action.response_type }}',
                                              '{{ action.short_description }}',
                                              '{{ action.modal_title }}',
                                              '{{ action.modal_ok }}',
                                              '{{ action.modal_cancel }}'
                                          );
                                      {% endif %}
                                  }
                              }
                          ]
                      }
                  ]
              }
          })

          $$('{{ view_prefix }}datatable').showOverlay("<img src='{% static 'django_webix/loading.gif' %}'>");
          var _params = $.extend({}, webixAppliedFilters['{{ model|getattr:'_meta'|getattr:'app_label'}}.{{ model|getattr:'_meta'|getattr:'model_name'}}']);
          _params['action'] = '{{ action_key }}';
          _params['csrfmiddlewaretoken'] = getCookie('csrftoken');
          _params['template_view'] = true;
          if (all === false) {
              _params['ids'] = ids.join(',');
          }
          $.ajax({
              url: "{{ url_list|safe }}",
              type: "POST",
              dataType: 'script',
              data: _params,
              error: function (jqXHR, textStatus, errorThrown) {
                  webix.message({
                      text: "{{ _("Action is not executable")|escapejs }}",
                      type: "error",
                      expire: 10000
                  });
                  $$('{{ view_prefix }}datatable').hideOverlay();
              },
              success: function (data) {
                  $$('{{ view_prefix }}datatable').hideOverlay();
                  templateViewWindow.show();
              }
          });
      }
    {% endif %}
{% endif %}
{% endfor %}


function {{ view_prefix }}actions_execute(action, ids, all) {
    {% block action_execute %}
    {% for layer in layers %}
    if (action=='gotowebgis_{{ layer.codename }}') {
        $$("map").goToWebgisPks('{{layer.qxsname}}', '{{ pk_field_name }}', ids, 'selectMode');
    } else if (action=='filtertowebgis_{{ layer.codename }}') {
        $$("map").goToWebgisPks('{{layer.qxsname}}', '{{ pk_field_name }}', ids, 'filterMode');
    }
    {% endfor %}
    {% for action_key, action in actions.items %} if (action=='{{ action_key }}') {
        {% if action.dynamic %}
            _{{ action_key }}_action_execute_dynamic(ids,all);
        {% elif action.template_view %}
            _{{ action_key }}_action_execute_template_view(ids,all);
        {% elif action.form %}
            _{{ action_key }}_action_execute_form(ids,all);
        {% else %}
            _{{ view_prefix }}action_execute(
                '{{ action_key }}',
                ids,
                all,
                '{{ action.response_type }}',
                '{{ action.short_description }}',
                '{{ action.modal_title }}',
                '{{ action.modal_ok }}',
                '{{ action.modal_cancel }}',
                null,
                null,
                null,
                {% if action.reload_list %}true{% else %}false{% endif %}
            );
        {% endif %}
    } {% if not forloop.last %} else {% endif %}

    {% endfor %}

    {% endblock %}

}
{% else %}
var {{ view_prefix }}actions_list = undefined;
var {{ view_prefix }}actions_execute = undefined;
{% endif %}
