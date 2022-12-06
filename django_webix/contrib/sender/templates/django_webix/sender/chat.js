{% load static i18n send_methods_utils %}

{% user_can_send as can_send %}

{% block content %}
    webix.ui([], $$('{{ webix_container_id }}'));

    $$("{{ webix_container_id }}").addView({
        cols: [
            {% if recipients|length > 1 or can_send %}
                {
                    rows: [
                        {
                            view: "search",
                            placeholder: "{{ _("Search..") }}",
                            on: {
                                onKeyPress: function(code, e) {
                                    var $this = this;
                                    setTimeout(function() {
                                        $$("recipients_list").filter(function(obj){
                                            return obj.representation.toString().toLowerCase().indexOf($this.getValue().toLowerCase()) != -1;
                                        });
                                    }, 10);
                                }
                            }
                        },
                        {
                              view: "list",
                              id: "recipients_list",
                              width: 320,
                              template: function(item) {
                                  return "<b>" + item.representation + "</b><br/><div style='display: inline-block; float: left;'>" + item.send_method.split('.', 1)[0] + "</div><div style='display: inline-block; float: right;'>" + item.last_message + "</div>";
                              },
                              type: {
                                  height:"auto"
                              },
                              select: "select",
                              on: {
                                  onItemClick: function(id, e, node) {
                                      var item = this.getItem(id);
                                      load_js("{% url 'dwsender.messages_chat' section='messages' %}?contenttype=" + item.contenttype + "&recipient=" + item.pk + "&send_method=" + item.send_method);
                                  }
                              },
                              data: [
                                  {% for recipient in recipients %}
                                      {
                                        pk: {{ recipient.id }},
                                        send_method: "{{ recipient.send_method }}",
                                        contenttype: "{{ recipient.contenttype }}",
                                        representation: "{{ recipient.representation }}",
                                        last_message: "{{ recipient.last_message|date }}"
                                      },
                                  {% endfor %}
                              ]
                          }
                    ]
                },
            {% endif %}
            {
                id: "messages",
                cols: []
            }
        ]
    });

    {% if recipients|length == 1 and not can_send %}
        load_js("{% url 'dwsender.messages_chat' section='messages' %}?contenttype={{ recipients.0.contenttype }}&recipient={{ recipients.0.id }}&send_method={{ recipients.0.send_method }}");
    {% endif %}
{% endblock %}
