{% load utils_getattr %}

{% if missing_realted %}
$$("{{view.webix_view_id|default:"content_right"}}").addView({
    'cols':[
        { $template:"Spacer"},
   {'width':450,'height': 60,'margin':20,'view':"template", 'type':"header",'css':'webix_error',
   'template':'<p style="font-size:18px;text-align:center !important;margin:0px;padding:0px;">Non puoi aggiungere {{object_list.model|getattr:"_meta"|getattr:"verbose_name_plural"}} <br>Devi prima aggiungere:</p>' },
        { $template:"Spacer" }
        ]
        });
  

{% for el in missing_realted %}
  $$("{{view.webix_view_id|default:"content_right"}}").addView({'cols':[
        { $template:"Spacer"},
        {'width':450, 'height':50, view:"button", id:'button_add_{{forloop.counter}}', type:"htmlbutton",label:"<span style='font-size:22px;'>Aggiungi {{el|getattr:"_meta"|getattr:"verbose_name"}}</span>"},
        { $template:"Spacer" }
        ]
        });
  $$("button_add_{{forloop.counter}}").attachEvent("onItemClick", function(id, e){
    load_js('{% url el.get_url_list %}');
    })
{% endfor %}


{% endif %}
