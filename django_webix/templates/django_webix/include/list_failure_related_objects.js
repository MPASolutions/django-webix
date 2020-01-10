{% load django_webix_utils i18n %}

$$("{{ webix_container_id }}").addView({
    id: "header_failure_related_objects",
    view: "template",
    template: "{% trans "These objects do not allow the requested operation" %}",
    type: "header"
});

var failure_related_objects = [
    {% for el in failure_related_objects %}
        {
            'id': "{{el.pk}}",
            'model': "{{el|getattr:"_meta"|getattr:"verbose_name"}}",
            'object': "{{el}}"
        }{% if not forloop.last %}, {% endif %}
    {% endfor %}
]
$$("{{webix_container_id}}").addView({
    id: 'list_failure_related_objects',
    view: "datatable",
    columns: [
        {id: "model", header: ["{% trans "Data type" %}", {content: "textFilter"}], fillspace: true},
        {id: "object", header: ["{% trans "Description" %}", {content: "textFilter"}], fillspace: true}
    ],
    data: webix.copy(failure_related_objects)
});
