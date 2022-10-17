List/Admin Actions
==================

ListView Actions
~~~~~~~~~~~~~~~~

Create the actions (e.g. <app_name>/actions.py) and load it into ListView or Admin.

.. code-block:: python

    from django.http import JsonResponse

    from django_webix.views.generic.decorators import action_config

    # list checkboxes actions
    @action_config(action_key='CUSTOMKEY',
                   response_type='json',
                   short_description='TEXT4')
                   allowed_permissions=['delete'],
                   reload_list=True,
                   maximum_count=None, # limit for action execution
                   modal_title="Are you sure you want to proceed with this action?",
                   modal_header="method for elaborate...",
                   modal_click='Elaborate',
                   modal_ok="Proceed",
                   modal_cancel="Undo",
                   form=ElabForm)
    def my_action(self, request, qs, form):
        data = form.cleaned_data
        qs.update(status='p')
        return JsonResponse({
            "status": True,
            "message": 'Updated {} items'.format(qs.count()),
            "redirect_url": self.get_url_list(),
        }, safe=False)

Javascript template
~~~~~~~~~~~~~~~~~~~

In javascript list template overwrite the `toolbar_list_actions` block

1. First of all write a new function with the action user interface definition, usually with some user input widgets (choices, text)

    * This function show the user input widgets windows, and then, on confirm callback, runs the action_execute function with the input params as last optional argument (all the other arguments are not changed)
    * The input params shoud be an object like: {'my_choice': 'choice_value'}

    .. code-block:: javascript

        var my_custom_action_ui = function (action, ids, all, response_type, short_description, modal_title, modal_ok, modal_cancel) {
            webix.ui({
                view: "window",
                width: 300,
                modal: true,
                position: "center",
                head: {
                    view: "label",
                    label: short_description,
                    align: "center",
                },
                body: {
                    view: "form",
                    rules: {
                        "my_choices_name": webix.rules.isNotEmpty,
                    },
                    elements: [
                        // INPUT TITLE
                        {template: "Select the desired value", borderless: true, css: {"text-align": "center"}, autoheight: true},
                        // INPUT WIDGETS
                        {
                            cols: [
                                {},
                                {
                                    view: "richselect",
                                    label: "Choices label",
                                    labelWidth: 100,
                                    width: 250,
                                    name: 'my_choices_name',   // name serve per rules, validate e get form elements
                                    invalidMessage: "Required to select a value",
                                    options: [
                                        {id: 'option_1', value: "Option 1"},
                                        {id: 'option_2', value: "Option 2"}
                                    ]
                                },
                                {}
                            ]
                        },
                        {height: 5},
                        // FOOTER WITH CENETERD BUTTONS: | Cancel | Send |
                        {
                            margin: 5,
                            cols: [
                                {},
                                {
                                    view: "button",
                                    width: 100,
                                    value: modal_cancel,
                                    click: function () {
                                        // returns the top parent view, for element in window: window
                                        this.getTopParentView().hide();
                                    }
                                },
                                {
                                    view: "button",
                                    width: 100,
                                    value: modal_ok,
                                    css: "webix_primary",
                                    click: function () {
                                        if (this.getFormView().validate()) {
                                            this.getTopParentView().hide();
                                            var params = {'my_choice': this.getFormView().elements["my_choices_name"].getValue()}
                                            _{{ view_prefix }}action_execute(
                                                action, ids, all, response_type, short_description, modal_title, modal_ok, modal_cancel, params
                                            )
                                        }
                                    }
                                },
                                {}
                            ]
                        }
                    ]
                }
            }).show();
        };

2. Then overwrite the `toolbar_list_actions` block to use `my_custom_action_ui`

    .. code-block:: javascript

        {% block toolbar_list_actions %}
            {% if is_enable_actions %}

                var {{ view_prefix }}actions_list = [
                    {% for action_key,action in actions.items %}
                        {id: '{{ action_key }}', value: '{{ action.short_description }}'}{% if not forloop.last %}, {% endif %}
                    {% endfor %}
                ];

                function {{ view_prefix }}actions_execute(action, ids, all) {
                    {% for action_key, action in actions.items %}
                        {% if action_key == 'my_action_name' %}
                            if (action == '{{ action_key }}') {
                                my_custom_action_ui(
                                    '{{ action_key }}',
                                    ids,
                                    all,
                                    '{{ action.response_type }}',
                                    '{{ action.short_description }}',
                                    '{{ action.modal_title }}',
                                    '{{ action.modal_ok }}',
                                    '{{ action.modal_cancel }}'
                                )
                            } {% if not forloop.last %} else {% endif %}
                        {% else %}
                            if (action == '{{ action_key }}') {
                                _{{ view_prefix }}action_execute(
                                    '{{ action_key }}',
                                    ids,
                                    all,
                                    '{{ action.response_type }}',
                                    '{{ action.short_description }}',
                                    '{{ action.modal_title }}',
                                    '{{ action.modal_ok }}',
                                    '{{ action.modal_cancel }}'
                                )
                            } {% if not forloop.last %} else {% endif %}
                        {% endif %}
                    {% endfor %}
                }
            {% else %}
                var {{ view_prefix }}actions_list = undefined;
                var {{ view_prefix }}actions_execute = undefined;
            {% endif %}
        {% endblock %}

Conclusions
~~~~~~~~~~~

Finally you can access the input parametrs as request POST data in the action method `my_action(self, request, qs)`

.. code-block:: python

    params = json.loads(request.POST['params'])
    choice_value = params['my_choice']
