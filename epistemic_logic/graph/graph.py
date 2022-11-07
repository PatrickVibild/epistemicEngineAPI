import networkx as nx
import matplotlib.pyplot as plt

from epistemic_logic.dynamic_epistemic_logic import DEL


def generate_graph(dynamic_epistemic_logic) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    for world in dynamic_epistemic_logic.worlds:
        G.add_node(world.name, predicates=str(world.assignment))
    for agent in dynamic_epistemic_logic.relations:
        edges = list(dynamic_epistemic_logic.relations[agent])
        G.add_edges_from(edges, A=agent)
    return G


def visualize_graph(G):
    nx.draw(G, with_labels=True)
    plt.show()


def find_solutions(G, from_world, too_world, limit):
    paths = nx.all_simple_paths(G, from_world, too_world, cutoff=limit)
    return paths
