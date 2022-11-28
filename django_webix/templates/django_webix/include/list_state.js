
function {{ view_prefix }}save_state() {
    webix.storage.local.put('{{ view_prefix }}datatable_state', {{ view_prefix }}get_state_ui());
}

function {{ view_prefix }}restore_state_grid() {
    {{ view_prefix }}datatable_disable_savestate = true;
    selector_grid = '{{ view_prefix }}datatable';
    var state = webix.storage.local.get(selector_grid + "_state");
    if (state) {
        try { // if list change for different user etc...
            $$(selector_grid).setState(state.grid);
        } catch (error) {
            {{ view_prefix }}drop_state();
        }
    }
}

function {{ view_prefix }}restore_initial_state() {
    selector_grid = '{{ view_prefix }}datatable';
    webix.storage.local.put('{{ view_prefix }}datatable_state', {{ view_prefix }}initial_state);
}

function {{ view_prefix }}restore_state_page() {
    selector_grid = '{{ view_prefix }}datatable';
    var state = webix.storage.local.get(selector_grid + "_state");
    if (state) {
        page = parseInt(state.page);
        $$(selector_grid).setPage(page);
    }
}

function {{ view_prefix }}get_state_ui() {
    selector_grid = '{{ view_prefix }}datatable';
    return {
        'grid': $$(selector_grid).getState(),
        'page': $$(selector_grid).getPage(),
    };
 }

function {{ view_prefix }}get_state() {
    selector_grid = '{{ view_prefix }}datatable';
    var state = webix.storage.local.get(selector_grid + "_state");
    if (state) {
        return state
    } else {
        return undefined
    }
}

function {{ view_prefix }}drop_state() {
    selector_grid = '{{ view_prefix }}datatable';
    var state = webix.storage.local.get(selector_grid + "_state");
    if (state) {
        return webix.storage.local.remove(selector_grid + "_state");
    }
}
