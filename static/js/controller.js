$("#graphdata").submit((e) => {
    $.ajax("/process_graph", {
        method: "post",
        dataType: "json"
        data: $("#graphdata").serialize(),
        success: (data, status, xhr) => {
            console.log(data);
            draw_graph(data["graph"]);
            load_data(data[""])
        }
    });
    return false;
});