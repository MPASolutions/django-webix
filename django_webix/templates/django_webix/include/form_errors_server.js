var errors = [];
{% block webix_form_errors %}
    {% for error in form.non_field_errors %}
        errors.push({"label":null, "error":"{{ error|safe|escapejs }}"});
    {% endfor %}
    {% for field in form %}
        {% for error in field.errors %}
            errors.push({"label":"{{ field.label|safe|escapejs }}", "error":"{{ error|safe|escapejs }}"});
        {% endfor %}
    {% endfor %}
{% endblock %}
{% block webix_inline_errors %}
    {% for inline in inlines %}
        {% for inline_form in inline %}
            {% with form=inline_form %}
                 {% for error in form.non_field_errors %}
                     errors.push({"label":null, "error":"{{ error|safe|escapejs }}"});
                {% endfor %}
                {% for field in form %}
                    {% for error in field.errors %}
                        errors.push({"label":"{{ field.label|safe|escapejs }}", "error":"{{ error|safe|escapejs }}"});
                    {% endfor %}
               {% endfor %}
            {% endwith %}
        {% endfor %}
    {% endfor %}
{% endblock %}
