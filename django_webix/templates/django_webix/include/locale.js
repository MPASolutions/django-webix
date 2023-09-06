{% load i18n %}

{% get_current_language as LANGUAGE_CODE %}

{% comment %}
https://docs.webix.com/api__i18n_setlocale.html
http://www.lingoes.net/en/translator/langcode.htm

"en-US" - North American (used by default);
{% endcomment %}

{% if LANGUAGE_CODE|slice:":2"|lower == 'it' %}
  webix.i18n.setLocale("it-IT");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'de' %}
  webix.i18n.setLocale("de-DE");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'en' %}
  webix.i18n.setLocale("en-US");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'es' %}
  webix.i18n.setLocale("es-ES");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'fr' %}
  webix.i18n.setLocale("fr-FR");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'ru' %}
  webix.i18n.setLocale("ru-RU");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'ja' %}
  webix.i18n.setLocale("ja-JP");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'be' %}
  webix.i18n.setLocale("be-BY");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'zh' %}
  webix.i18n.setLocale("zh-CN");
{% elif LANGUAGE_CODE|slice:":2"|lower == 'pt' %}
  webix.i18n.setLocale("pt-BR");
{% endif %}
