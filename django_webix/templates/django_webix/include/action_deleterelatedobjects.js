{% load i18n %}

$$('{{ webix_container_id }}').addView({
    view: "template",
    autoheight: true,
    borderless: true,
    template: function (obj) {
        var text = '<p>{{ _("The following objects will be deleted")|escapejs }}:</p>';
        text += '<ul>';

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
$$('{{ webix_container_id }}').addView({
    view: "tree",
    borderless: true,
    height: 350,
    data: JSON.parse("{{ related_objects|safe|escapejs }}")
});
