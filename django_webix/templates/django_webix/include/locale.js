{% load i18n %}

{% get_current_language as LANGUAGE_CODE %}
{% if LANGUAGE_CODE == 'it' %}
webix.i18n.setLocale("it-IT");
{% endif %}
{% if LANGUAGE_CODE == 'de' %}
webix.i18n.setLocale("de-DE");
{% endif %}
{% if LANGUAGE_CODE == 'en' %}
webix.i18n.setLocale("en-US");
{% endif %}
{% if LANGUAGE_CODE == 'es' %}
webix.i18n.setLocale("es-ES");
{% endif %}
{% if LANGUAGE_CODE == 'fr' %}
webix.i18n.setLocale("fr-FR");
{% endif %}
