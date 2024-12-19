
        $$("{{ webix_container_id }}").addView({
            cols:[

                {
                 {% if request.user_agent.is_mobile %}hidden: true,{% endif %}
                 width:360,
                 cols:[
                    {
                        id: '{{ view_prefix }}select_all_button',
                        view: 'button',
                        css:'webix_danger',
                        value: '{{ _("Select all")|escapejs }}',
                        width:120,
                        hidden: true,
                        click: function (id, event) {
                            $$('{{ view_prefix }}select_all_checkbox').setValue(1);
                            {{ view_prefix }}update_counter();
                        }
                    },
                    {
                        id: '{{ view_prefix }}unselect_all_button',
                        view: 'button',
                        value: '{{ _("Cancel selection")|escapejs }}',
                        width:120,
                        hidden: true,
                        click: function (id, event) {
                            $$('{{ view_prefix }}select_all_checkbox').setValue(0);
                            $$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox").uncheck();
                            {{ view_prefix }}update_counter();
                        }
                    },
                    {id: '{{ view_prefix }}select_all_checkbox', view: 'checkbox', value: 0, hidden:true},
                    {id: '{{ view_prefix }}stats_list', view: 'label', label: '',width:230},
                    ]
                },

                {
                    cols:[
                        {
                            {% if request.user_agent.is_mobile %}hidden: true,{% endif %}
                        },
                        {%  if is_json_loading %}
                        {
                            template: "{common.first()} {common.prev()} {common.pages()} {common.next()} {common.last()}",
                            id: "{{ view_prefix }}datatable_pager", // the container to place the pager controls into
                            view: "pager",
                            hidden: true,
                            {% if not request.user_agent.is_mobile %}minWidth: 460,{% endif %}
                            group: 4, // buttons for next and back
                            css: {'text-align':'center'},
                            // must to be the same of url request because managed from interface
                            size: {{ paginate_count_default }},
                            page: {{ view_prefix }}initial_page,
                            on: {
                                onBeforePageChange: function (new_page, old_page) {
                                    if ($$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox") != undefined && $$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox").isChecked() == true) {
                                        $$('{{ view_prefix }}datatable').getHeaderContent("id_{{ view_prefix }}master_checkbox").check();
                                        {{ view_prefix }}update_counter();
                                    }
                                }
                            }
                        },
                        {% endif %}
                        {
                            {% if request.user_agent.is_mobile %}hidden: true,{% endif %}
                        }
                    ]
                },

                {
                    width:360,
                    {% if request.user_agent.is_mobile %}hidden: true,{% endif %}
                    $template: "Spacer"
                },
            {%  if is_json_loading %}
                {
                    id: '{{ view_prefix }}datatable_pager_goto',
                    cols:[
                        {
                            view:"text",
                            name:"goto_page",
                            id:"goto_page",
                            width:70,
                            pattern:{ mask:'#'.repeat(Math.pow(2,10)), allow:/[0-9]/g}
                        },
                        {
                            view:"button",
                            value:"{{ _("Go")|escapejs }}",
                            width:40,
                            align:"right",
                            on: {
                                onItemClick: function (id, e, node){
                                    $$('{{ view_prefix }}datatable').setPage($$('goto_page').getValue()-1);
                                }
                            }
                        },
                    ]
                }
            {% endif %}

            ]
        })
