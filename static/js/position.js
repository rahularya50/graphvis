const D = 200;
const K1 = 0.1;
const K2 = 100000;

const MIN_FORCE = 1;

const DAMPING = 0.5;

function dist(v1, v2) {
    return Math.pow(Math.pow(v1.x - v2.x, 2) + Math.pow(v1.y - v2.y, 2), 0.5)
}

function position(vertex_pos, vertex_vel, edges) {
    let forces = [];
    for (let i = 0; i !== vertex_pos.length; ++i) {
        forces.push({"x": 0, "y": 0});
    }
    for (let edge of edges) {
        let a = edge[0];
        let b = edge[1];
        let d = dist(vertex_pos[a], vertex_pos[b]);
        let F = K1 * (d - D);
        forces[a].x += F * (vertex_pos[b].x - vertex_pos[a].x) / d;
        forces[a].y += F * (vertex_pos[b].y - vertex_pos[a].y) / d;
        forces[b].x += F * (vertex_pos[a].x - vertex_pos[b].x) / d;
        forces[b].y += F * (vertex_pos[a].y - vertex_pos[b].y) / d;
    }
    for (let i = 0; i !== vertex_pos.length; ++i) {
        for (let j = 0; j !== vertex_pos.length; ++j) {
            if (i === j) {
                continue;
            }
            forces[i].x += K2 / Math.pow(dist(vertex_pos[i], vertex_pos[j]), 3) * (vertex_pos[i].x - vertex_pos[j].x);
            forces[i].y += K2 / Math.pow(dist(vertex_pos[i], vertex_pos[j]), 3) * (vertex_pos[i].y - vertex_pos[j].y);
            forces[j].x += K2 / Math.pow(dist(vertex_pos[i], vertex_pos[j]), 3) * (vertex_pos[j].x - vertex_pos[i].x);
            forces[j].y += K2 / Math.pow(dist(vertex_pos[i], vertex_pos[j]), 3) * (vertex_pos[j].y - vertex_pos[i].y);
        }
    }
    let stop = true;
    for (let i = 0; i !== forces.length; ++i) {
        vertex_vel[i].x *= DAMPING;
        vertex_vel[i].y *= DAMPING;
        vertex_vel[i].x += forces[i].x;
        vertex_vel[i].y += forces[i].y;
        if (Math.pow(forces[i].x, 2) + Math.pow(forces[i].y, 2) > Math.pow(MIN_FORCE, 2)) {
            stop = false;
        }
    }
    for (let i = 0; i !== vertex_pos.length; ++i) {
        vertex_pos[i].x += vertex_vel[i].x;
        vertex_pos[i].y += vertex_vel[i].y;
    }
    return [vertex_pos, vertex_vel, stop];
}