{% load django_webix_utils %}

{% block webix_content %}

    {% block context_cleaner %}
    webix.ui([], $$("{{ webix_container_id }}"));
    {% endblock %}

    {% block toolbar_navigation %}
        {% if url_update and url_update != '' %}
            {% include "django_webix/include/toolbar_navigation.js" with url_back=url_update %}
        {% elif url_list and url_list != '' %}
            {% include "django_webix/include/toolbar_navigation.js" with url_back=url_list %}
        {% endif %}
    {% endblock %}

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
                view: "tootipButton",
                type: "form",
                align: "right",
                id: "delete",
                label: "Conferma cancellazione",
                width: 200,
                click: function () {
                    $.ajax({
                        url: "{{ url_delete }}",
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
