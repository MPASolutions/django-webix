{% extends "django_webix/generic/list.js" %}

{% block webix_content %}
  function typeIcon(el) {
    if (el.icon === 'pdf') {
      return "<div><i style='cursor: pointer' class='webix_icon fas fa-file-pdf'></i></div>"
    }
    else if (el.icon === 'video') {
      return "<div><i style='cursor: pointer' class='webix_icon fas fa-video'></i></div>"
    }
  }

  function popup_video(url) {
    webix.ui({
      view: "window",
      height: Math.max($(window).height() / 100 * 80, 600),
      width: Math.max($(window).width() / 100 * 80, 800),
      modal: true,
      move: true,
      resize: true,
      position: "center",
      head: {
        view: "toolbar",
        cols: [
          {view: "label", label: "{{_("Video tutorial")|escapejs}}"},
          {
            view: "icon", icon: "fas fa-window-close", click: function () {
              $$(this).getParentView().getParentView().destructor();
            }
          }
        ]
      },
      body: {
        view: "iframe",
        id: "frame-body",
        src: url + "?autoplay=1&modestbranding=1&rel=0&showinfo"
      }
    }).show();
  }

  function popup_pdf(url) {
    webix.ui({
      view: "window",
      height: Math.max($(window).height() / 100 * 80, 600),
      width: Math.max($(window).width() / 100 * 80, 800),
      modal: true,
      move: true,
      resize: true,
      position: "center",
      head: {
        view: "toolbar",
        cols: [
          {view: "label", label: "{{_("PDF tutorial")|escapejs}}"},
          {
            view: "icon", icon: "fas fa-window-close", click: function () {
              $$(this).getParentView().getParentView().destructor();
            }
          }
        ]
      },
      body: {
        type: "space",
        rows: [
          {view: "pdfbar", id: "toolbar"},
          {
            view: "pdfviewer",
            id: "pdf",
            toolbar: "toolbar",
            url: "binary->" + url
          }
        ]
      }
    }).show();
  }

  {{ block.super }}

  $$('{{ view_prefix }}datatable').hideColumn("checkbox_action");

{% endblock %}

{% block datatable_onitemclick %}
  if (el.target === '_self' || el.target === '_blank') {
    window.open(el.url, el.target);
  } else if (el.target === 'iframe') {
    if (el.tutorial_type === 'pdf') {
      popup_pdf(el.url);
    }
    else if (el.tutorial_type === 'video') {
      popup_video(el.url);
    }
  }
{% endblock %}

{% block datatable_columns_commands %}{% endblock %}
{% block toolbar_list %}{% endblock %}
