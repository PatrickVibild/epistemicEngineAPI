from epistemic_logic.dynamic_epistemic_logic import DEL
import time
import matplotlib.pyplot as plt

from main import return_world


def experiment(runs, max_w):
    agents = ["SALLY", "ANNIE"]

    vision = [
        ["ANNIE", "SALLY"],
        ["SALLY", "ANNIE"]
    ]

    n_worlds = []
    n_relations = []
    n_times = []
    DEL.reset()
    DEL.set_max_worlds(max_w)
    for i in range(runs):
        start = time.time()
        DEL.update_vision(vision)
        DEL.update(agents[i % 2], 'IN(cube{0},box1)'.format(str(i)))
        # output = return_world()
        DEL.remove_vision(vision)
        DEL.update(agents[(i + 1) % 2], 'IN(cube{0},box2) AND ~IN(cube{1},box1)'.format(str(i), str(i)))
        DEL.world_cap()
        # output = return_world()
        if i % 1 == 0:
            runtime = time.time() - start
            relations = 0
            for agent in DEL.relations:
                relations += len(DEL.relations[agent])
            n_worlds.append(len(DEL.worlds))
            n_relations.append(relations)
            n_times.append(runtime)
            print('Run {0}: Worlds - {1}, Relations - {2}, Computation time - {3}'.format(str(i), str(len(DEL.worlds)),
                                                                                          str(relations), str(runtime)))
    return n_worlds, n_relations, n_times


if __name__ == '__main__':
    runs = 15
    n1, r1, t1 = experiment(runs, -1)
    n2, r2, t2 = experiment(runs, 2048)
    runs_iteration = list(range(1, runs + 1))

    plt.plot(runs_iteration, n2, label='Default')
    plt.plot(runs_iteration, n1, label='World Clipping')
    plt.xlabel('Number of false beliefs')
    plt.ylabel('Number of possible worlds')
    plt.legend(loc="upper left")
    plt.show()

    plt.plot(runs_iteration, t2, label='Default')
    plt.plot(runs_iteration, t1, label='World Clipping')
    plt.xlabel('Number of false beliefs')
    plt.ylabel('Execution time adding X+1 event')
    plt.legend(loc="upper left")
    plt.show()


