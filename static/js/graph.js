// create a wrapper around native canvas element (with id="c")
let canvas = new fabric.Canvas('canvas');
canvas.selection = false;
let nodes = []; // [node canvas objects]
let edges = []; // [vertex_index -> [edge canvas object, edge label canvas object]]
let graph = []; // [vertex_index -> [adjacent vertex indices]

let vertex_pos = []; // [{"x" : x, "y" : y}]
let vertex_vel = []; // [{"x" : x, "y" : y}]
let edge_list = []; // [[v_index_1, v_index_2]]

const RADIUS = 20;

const LEFT = 50;
const TOP = 50;
const RIGHT = 450;
const BOTTOM = 450;

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
    vertex_pos.push({"x": x, "y": y});
    vertex_vel.push({"x": 0, "y": 0});
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
    edge_list.push([i, j]);
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

function placeNode(i, x, y) {
    nodes[i].set({"left": x, "top": y});
    nodes[i].setCoords();
    canvas.renderAll();
    redrawEdges(i);
    canvas.renderAll();
}

function positionNodes(now) {
    let stop;
    for (let i = 0; i !== 5; ++i) {
        [vertex_pos, vertex_vel, stop] = position(vertex_pos, vertex_vel, edge_list);
    }

    let xMin = Math.min(...vertex_pos.map(pos => pos.x));
    let xMax = Math.max(...vertex_pos.map(pos => pos.x));
    let yMin = Math.min(...vertex_pos.map(pos => pos.y));
    let yMax = Math.max(...vertex_pos.map(pos => pos.y));

    for (let i = 0; i !== nodes.length; ++i) {
        placeNode(i,
            (vertex_pos[i].x - xMin) / (xMax - xMin) * (RIGHT - LEFT) + LEFT / 2,
            (vertex_pos[i].y - yMin) / (yMax - yMin) * (BOTTOM - TOP) + TOP / 2);
    }
    canvas.renderAll();
    if (stop) {
        return;
    }
    requestAnimationFrame(positionNodes);
}

function draw_graph(g) {
    canvas.clear();
    nodes = [];
    edges = [];
    graph = [];
    vertex_pos = [];
    edge_list = [];
    console.log(g);
    for (let vertex of g["vertices"]) {
        addNode(vertex["name"], vertex["x"], vertex["y"]);
    }
    for (let edge of g["edges"]) {
        addEdge(edge["head"], edge["tail"], "")
    }
    requestAnimationFrame(positionNodes);
}