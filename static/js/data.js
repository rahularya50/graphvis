let vargraph;
let varvals;
let active_vars;

$("#add_var").click(() => {

});

function load_data(vgraph, vvals) {
    vargraph = vgraph;
    varvals = vvals;
    active_vars = new Set();
}

function get_vars() {
    let out = [];

    for (let v of vargraph) {
        if (active_vars.has(v)) {
            continue;
        }
        let ok = true;
        for (let ancestor of vargraph[v]) {
            if (!active_vars.has(ancestor)) {
                ok = false;
                break;
            }
        }
        if (ok) {
            out.push(v);
        }
    }

    return out;
}

function select_var(v) {
    active_vars.push(v);
}
