{% load django_webix_utils %}

{% block webix_content %}

    {% block context_cleaner %}
    webix.ui([], $$("{{ webix_container_id }}"));
    {% endblock %}

    {% if url_update and url_update != '' %}
        {% url url_update object.pk as url_back %}
        {% include "django_webix/include/toolbar_navigation.js" with url_back=url_back %}
    {% elif url_list and url_list != '' %}
        {% url url_list as url_back %}
        {% include "django_webix/include/toolbar_navigation.js" with url_back=url_back %}
    {% endif %}

    {% if failure_delete_related_objects %}
        {% block failure_related_objects %}
        {% include "django_webix/include/list_failure_related_objects.js" with failure_related_objects=failure_delete_related_objects %}
        {% endblock %}
    {% endif %}

    {% if has_delete_permission %}
        $$("{{ webix_container_id }}").addView({
            view: "template",
            template: "Le seguenti schede verranno eliminate",
            type: "header",
        });

        $$("{{ webix_container_id }}").addView({
            view: "tree",
            data: JSON.parse("{{ related_objects|safe|escapejs }}"),
            on: {
                onItemClick: function (id, e, node) {
                    var item = this.getItem(id);
                    if ('url' in item) {
                        load_js(item.url);
                    }
                }
            }
        });
    {% endif %}

    {% if has_delete_permission and url_delete and url_delete != '' %}
    $$("{{ webix_container_id }}").addView({
        margin: 5,
        height: 30,
        view: "toolbar",
        cols: [
            {$template: "Spacer"},
            {
                view: "button",
                type: "form",
                align: "right",
                id: "delete",
                label: "Conferma cancellazione",
                width: 200,
                click: function () {
                    $.ajax({
                        url: "{% url url_delete object.pk %}",
                        dataType: "script",
                        type: "POST",
                        success: function () {
                            webix.ui.resize()
                        }
                    });
                }
            }
        ]
    });
    {% endif %}

    {% block extrajs_post %}{% endblock %}

{% endblock %}
