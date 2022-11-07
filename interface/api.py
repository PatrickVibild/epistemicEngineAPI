from flask import Flask, request
from epistemic_logic.dynamic_epistemic_logic import DEL
from epistemic_logic.graph.graph import *
import matplotlib as pl
import networkx as nx

app = Flask(__name__)


@app.route('/query_worlds_number', methods=['GET'])
def query_worlds():
    content = request.json
    try:
        from_world = int(content["from_world"])
        too_world = int(content["too_world"])
    except:
        return 'missing arguments', 400
    G = generate_graph(DEL)
    paths = find_solutions(G, from_world, too_world, DEL.world_nr + 1)
    print(list(paths))
    return paths, 200


@app.route('/event', methods=['POST'])
def new_world():
    content = request.json
    try:
        agent = content["agent"].upper()
        event = content["event"].upper()
    except:
        return 'missing arguments', 400
    DEL.update(agent, event)
    # TODO return information
    return "good", 200


@app.route('/sees', methods=['GET'])
def get_sees():
    return DEL.vision


@app.route('/sees', methods=['POST'])
def add_sees():
    try:
        content = request.json
        DEL.update_vision(content["sees"])
    except Exception as e:
        return str(e), 500
    return DEL.vision, 200


@app.route('/sees', methods=['DELETE'])
def delete_sees():
    try:
        content = request.json
        DEL.remove_vision(content["sees"])
    except Exception as e:
        return str(e), 500
    return DEL.vision, 200


@app.route('/reset', methods=['PUT'])
def reset():
    try:
        DEL.reset()
        return "DEL-reseted", 200
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
