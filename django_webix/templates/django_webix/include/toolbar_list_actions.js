{% load i18n %}

var {{ view_prefix }}toolbar_actions = [{
  view:"menu",
  id: "{{ view_prefix }}actions_menu",
  data:{{ view_prefix }}actions_list,
  on:{
    onMenuItemClick:function(id){
        item = this.getMenuItem(id);
        if (item.disable==undefined) {
            {{ view_prefix }}prepare_actions_execute(item.id);
        }
    }
  },
  type:{
    {% block type %}
    height:{% if request.user_agent.is_mobile %}35{% else %}55{% endif %},
    template:function(obj){
        var _template = '<p style="padding:{% if request.user_agent.is_mobile %}10{% else %}13{% endif %}px 5px 0px 5px;margin:0px">' + obj.value;
        if (obj.submenu!=undefined){
            _template += '<span class="webix_submenu_icon"></span>';
        }
        _template += '</p>';
        return _template
        }
    {% endblock %}
  }
}];
