from flask import Flask, request
from epistemic_logic.dynamic_epistemic_logic import DEL

app = Flask(__name__)


@app.route('/maxworlds', methods=['POST'])
def max_worlds():
    content = request.json
    DEL.set_max_worlds(int(content["max"]))
    return 'OK', 200
@app.route('/event', methods=['POST'])
def new_world():
    content = request.json
    try:
        agent = content["agent"].upper()
        event = content["event"].upper()
    except:
        return 'missing arguments', 400
    DEL.update(agent, event)
    DEL.crunch_worlds()
    agent_knowledge = DEL.knowledge(DEL.world_nr + 1)
    output = {}
    for knowledge in agent_knowledge:
        output[knowledge.agent] = knowledge.stringify()
    output["world"] = [str(predicate) for predicate in DEL.current_world.assignment]
    return output, 200


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

    app.run(host='0.0.0.0', port=5500)
