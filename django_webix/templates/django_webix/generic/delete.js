{% load django_webix_utils i18n %}

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

    {% if not has_delete_permission %}
    $$("{{ webix_container_id }}").addView({
        id: "header_failure_related_objects",
        view: "template",
        template: "{{ info_no_delete_permission|join:", "|escapejs }}",
        type: "header"
    });
    {% endif %}

    {% if failure_delete_blocking_objects %}
        {% block failure_blocking_objects %}
            {% include "django_webix/include/list_failure_blocking_objects.js"  with failure_blocking_objects=failure_delete_blocking_objects %}
        {% endblock %}
    {% else %}
        {% if failure_delete_related_objects %}
            {% block failure_related_objects %}
                {% include "django_webix/include/list_failure_related_objects.js" with failure_related_objects=failure_delete_related_objects %}
            {% endblock %}
        {% endif %}
    {% endif %}

    {% if has_delete_permission %}
        $$("{{ webix_container_id }}").addView({
            view: "template",
            template: '{{_("The following objects will be deleted")|escapejs}}',
            type: "header"
        });

        $$('{{ webix_container_id }}').addView({
            view: "template",
            autoheight: true,
            borderless: true,
            template: function (obj) {
                var text = '<ul>';

                {% for item in related_summary %}
                    text += '<li><b>{{ item.model_name }}</b>: {{ item.count }}</li>';
                {% endfor %}
                text += '</ul>';

                return text;
            }
        });

        $$('{{ webix_container_id }}').addView({
            view: "template",
            type: "section",
            css: {'font-size': '14px'},
            template: "{{ _("Details")|escapejs  }}"
        });

        $$("{{ webix_container_id }}").addView({
            view: "tree",
            id: "{{ object|getattr:"_meta"|getattr:"model_name" }}",
            data: JSON.parse("{{ related_objects|safe|escapejs }}"),
            on: {
                onItemClick: function (id, e, node) {
                    var item = this.getItem(id);
                    if ('url' in item) {
                        load_js(item.url, undefined, undefined, undefined, undefined, undefined, undefined, abortAllPending=true);
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
                    label: "{{_("Confirm cancellation")|escapejs}}",
                    width: 200,
                    click: function () {
                        {% if multiple_delete_confirmation == True %}
                            if ($$("{{ object|getattr:"_meta"|getattr:"model_name" }}").count() > 1) {
                                webix.confirm({
                                    title: "{{_("Delete confirmation")|escapejs}}",
                                    text: "{{_("Warning! All linked objects will also be deleted.")|escapejs}}",
                                    type: "confirm-alert"
                                }).then(function(result){
                                    load_js("{{ url_delete|safe }}", undefined, undefined, 'POST', undefined, undefined, undefined, abortAllPending=true);
                                })
                            } else {
                                load_js("{{ url_delete|safe }}", undefined, undefined, 'POST', undefined, undefined, undefined, abortAllPending=true);
                            }
                        {% else %}
                            load_js("{{ url_delete|safe }}", undefined, undefined, 'POST', undefined, undefined, undefined, abortAllPending=true);
                        {% endif %}
                    }
                }
            ]
        });
    {% endif %}

    {% block extrajs_post %}{% endblock %}

{% endblock %}
