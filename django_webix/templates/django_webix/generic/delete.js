webix.ui([], $$('{{ view.webix_view_id|default:"content_right" }}'));

{% if related %}
    {% include "django_webix/include/list_no_delete.js" %}
{% else %}
    {% include "django_webix/include/toolbar_buttons_delete.js" %}
{% endif %}
