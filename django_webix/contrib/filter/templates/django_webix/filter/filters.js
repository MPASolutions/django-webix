{% load static i18n %}

webix.ui([], $$("{{ webix_container_id }}"));

$$("{{ webix_container_id }}").addView({
    rows: [{
        id: "querybuilder-container",
        view: 'scrollview',
        scroll: 'y',
        body: {
            rows: [
                {
                    view: "jquery-querybuilder",
                    id: "querybuilder",
                    modelStart: "myapp.book",
                    filtersUrl: "{% url 'dwfilter.filter_config' app_label='app_label' model_name='model_name' %}",
                    suggestUrl: "{% url 'dwfilter.suggest_exact' field='field' %}",
                    limit_suggest: {{ limit_suggest }},
                    autocomplete_always: "{{ autocomplete_always }}",
                    icons: {
                        add_group: "fas fa-plus-circle",
                        add_rule: "fas fa-plus",
                        remove_group: "fas fa-times",
                        remove_rule: "fas fa-times",
                        error: "fas fa-exclamation-triangle"
                    },
                    plugins: {
                        sortable: {
                            icon: "fas fa-sort"
                        },
                        'not-group': {}
                    }
                }
            ]
        }
    }]
});

