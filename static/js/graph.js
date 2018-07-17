// create a wrapper around native canvas element (with id="c")
let canvas = new fabric.Canvas('canvas');
canvas.selection = false;
let nodes = [];
let edges = [];
let graph = [];

const RADIUS = 20;

function addNode(val, x, y) {
    let nodeShape = new fabric.Circle({
        radius: RADIUS,
        stroke: "black",
        fill: "white",
        originX: "center",
        originY: "center"
    });

    let nodeVal = new fabric.Text(val.toString(), {
        fontSize: 30,
        originX: "center",
        originY: "center"
    });

    let node = new fabric.Group([nodeShape, nodeVal], {
        left: x,
        top: y,
        lockScalingX: true,
        lockScalingY: true,
        lockRotation: true,
        hasControls: false,
        hasBorders: false,
    });

    canvas.add(node);
    nodes.push(node);
    graph.push([]);
    edges.push([]);
    let i = nodes.length - 1;
    node.on("moving", (e) => redrawEdges(i));
}

function addEdge(i, j, v) {
    let startX = nodes[i].left + RADIUS;
    let startY = nodes[i].top + RADIUS;
    let endX = nodes[j].left + RADIUS;
    let endY = nodes[j].top + RADIUS;

    let path = new fabric.Line([startX, startY, endX, endY], {
        stroke: "black",
        selectable: false,
        hoverCursor: "cursor"
    });
    canvas.add(path);
    canvas.sendToBack(path);
    let label = new fabric.Text(v.toString(), {
        fontSize: 30,
        left: (startX + endX) / 2,
        top: (startY + endY) / 2,
        selectable: false,
        hoverCursor: "cursor"
    });
    canvas.add(label);
    graph[i].push(j);
    graph[j].push(i);
    edges[i].push([path, label]);
    edges[j].push([path, label]);
}

function redrawEdges(i) {
    for (let x = 0; x !== graph[i].length; ++x) {
        let j = graph[i][x];
        let e = edges[i][x][0];
        let startX = nodes[i].left + RADIUS;
        let startY = nodes[i].top + RADIUS;
        let endX = nodes[j].left + RADIUS;
        let endY = nodes[j].top + RADIUS;
        e.set({'x1' : startX, 'y1' : startY, 'x2' : endX, 'y2' : endY});
        e.setCoords();
        edges[i][x][1].set({"left" : (startX + endX) / 2, "top" : (startY + endY) / 2});
        edges[i][x][1].setCoords();
    }
}

function draw_graph(g) {
    canvas.clear();
    nodes = [];
    edges = [];
    graph = [];
    console.log(g);
    for (let vertex of g["vertices"]) {
        addNode(vertex["name"], vertex["x"], vertex["y"]);
    }
    for (let edge of g["edges"]) {
        addEdge(edge["head"], edge["tail"], "")
    }
}