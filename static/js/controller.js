$("#graphdata").submit((e) => {
    $.post("/process_graph", $("#graphdata").serialize());
    return false;
});