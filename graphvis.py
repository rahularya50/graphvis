# coding=utf-8
from flask import Flask, send_from_directory, request

import endpoint

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/graphtest')
def graph_test():
    return send_from_directory("static", "index.html")


@app.route("/process_graph", methods=["POST"])
def process_graph():
    S = request.form.get("graphdata")
    fmt = request.form.get("graphformat")
    data = endpoint.get_data(fmt, S)
    return data


if __name__ == '__main__':
    app.run(debug=True)
