$("#graphdata").submit((e) => {
    $.ajax("/process_graph", {
        method: "post",
        dataType: "json",
        data: $("#graphdata").serialize(),
        success: (data, status, xhr) => {
            draw_graph(data["graph"]);
        }
    });
    return false;
});