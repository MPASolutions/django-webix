{% load i18n %}

var {{ view_prefix }}toolbar_actions = [{
  view:"menu",
  id: "{{ view_prefix }}actions_menu",
  data:{{ view_prefix }}actions_list,
  autowidth: true,
  on:{
    onMenuItemClick:function(id){
        item = this.getMenuItem(id);
        if (item.disable==undefined) {
            {{ view_prefix }}prepare_actions_execute(item.id);
        }
    }
  },
  {% block type %}
  css: 'actionToolbar',
  // another style to have separated buttons
  // css: 'actionToolbarButtons',
  type: {
      subsign:true,
  },
  {% endblock %}
}];
