{% load static i18n humanize send_methods_utils %}
{% if message_unread %}
var message_attachments = [
    {% for a in message_unread.message_sent.attachments.all %}
    {'id':'{{ a.pk }}','file':'{{ a.file }}','filename': '{{a.file.name}}', 'read':false},
    {% endfor %}
];

webix.ui({
    view: "window",
    id: "popup_messages_win",
    width: 1000,
    height: 400,
    scrool: 'y',
    position: "center",
    modal: true,
    head: {
        view: "toolbar",
        cols: [
            {view: "label", label: '{{_("Hi, there are messages to read...")|escapejs}}'},
            {
                view: "button",
                label: '{{_("Close")|escapejs}}',
                width: 100,
                align: 'right',
                click: "$$('popup_messages_win').destructor();"
            }
        ]
    },
    body: {
        rows: [
            {
                id: "message",
                type: {height: "auto"},
                template: '<div style="padding:10px;font-size:20px;float:none;color:#000 !important;">' +
                    "<span style='font-size: x-small; float: right'>{{ message_unread.creation_date|naturaltime }}</span>" +
                    '{{ message_unread.message_sent.body|linebreaksbr }}</div>'
            },
            {% if message_unread.message_sent.attachments.exists %}
            { view:"template", template:"{{_("Click and open each file before confirming the reading of this communication")}}", type:"header" },
            {
                id: "message_attachments",
                view: "list",
                autoheight: true,
                scroll: "auto",
                data: message_attachments,
                template:"#filename#",
                on:{
                    "onItemClick":function(id, e, node){
                        var item = this.getItem(id);
                        item['read']=true;
                        $$("message_attachments").updateItem(id, item);
                        window.open('{% get_media_prefix %}'+item.file, '_blank');
                    }
                }
            },
            {% endif %}
            {
                view: "toolbar", cols: [
                    {},
                    {
                        id: 'read_confirmation',
                        view: "button",
                        value: "{{_("I confirm that<br/>I have read")|escapejs}}",
                        type: "htmlbutton",
                        css: "home_buttons green",
                        height: 70,
                        width: 200,
                        click: function () {
                            var test = true;
                            for (var i = 0; i < message_attachments.length; i++){
                                if (message_attachments[i].read==false){
                                    test = false;
                                }
                            }
                            if (test==false){
                                webix.message({
                                    text:"{{_("You have not seen all the attachments.")|escapejs}}",
                                    type:"error",
                                    expire: 10000,
                                });
                            } else {
                                $$('popup_messages_win').destructor();
                                $.ajax({
                                    type: "POST",
                                    dataType: "script",
                                    cache: false,
                                    data: {'message_read_id':'{{message_unread.id}}'},
                                    url: "{% url 'dwsender.message_unread' %}",
                                });
                            }
                        }
                    },

                ]
            }
        ]
    }
}).show();
{% endif %}
