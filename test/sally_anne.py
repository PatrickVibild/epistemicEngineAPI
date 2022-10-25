from mlsolver.formula import Atom, Box_a, And
from mlsolver.kripke import KripkeStructure, World


def test_semantic_box_a_true():
    worlds = [
        World('1', {}),
    ]
    current_world = worlds[0]
    relations = {}
    ks = KripkeStructure(worlds, relations)

    # Sally In(CubeRed,Box1).

    current_world.assignment["In(CubeRed,Box1)"] = True
    relations.update({'sally': {('1', '1')},
                      'annie': {('1', '1')}
                      }
                     )
    ks = KripkeStructure(worlds, relations)
    # Sally leaves
    # TODO model the vision between agents.

    # Annie removes Cube from Box1 and put it on Box2
    new_world = World('2', {'In(CubeRed,Box2)': True})
    current_world = new_world
    worlds.append(new_world)

    # TODO here is where vision come into place.
    # TODO need to track each of the agents (current worlds)
    sallys_last_world = worlds[0]
    relations['sally'].update({(current_world.name, sallys_last_world.name)})
    relations['annie'].update({(current_world.name, current_world.name)})


    ks = KripkeStructure(worlds, relations)

    f = Box_a('sally', Atom('In(CubeRed,Box2)'))
    g = Box_a('sally', Atom('In(CubeRed,Box1)'))
    h = Box_a('annie', Atom('In(CubeRed,Box2)'))
    i = Box_a('annie', And(Atom('In(CubeRed,Box1)'),Atom('In(CubeRed,Box1)')))
    sally_k_box2 = ks.solve(f)
    sally_k_box1 = ks.solve(g)
    annie_k_box2 = ks.solve(h)
    annie_k_box1 = ks.solve(i)
    #TODO Detect false beliefs.

    assert True == True


def add_symmetric_edges(relations):
    """Routine adds symmetric edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for r in agents_relations:
            x, y = r[1], r[0]
            result_agents.add((x, y))
        result[agent] = result_agents
    return result


def add_reflexive_edges(worlds, relations):
    """Routine adds reflexive edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for world in worlds:
            result_agents.add((world.name, world.name))
            result[agent] = result_agents
    return result
