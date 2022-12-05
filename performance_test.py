from epistemic_logic.dynamic_epistemic_logic import DEL
import time

from main import return_world


def experiment(runs):
    agents = ["SALLY", "ANNIE"]

    vision = [
        ["ANNIE", "SALLY"],
        ["SALLY", "ANNIE"]
    ]

    for i in range(runs):
        start = time.time()
        DEL.update_vision(vision)
        DEL.update(agents[i % 2], 'IN(cube{0},box1)'.format(str(i)))
        # output = return_world()
        DEL.remove_vision(vision)
        DEL.update(agents[(i + 1) % 2], 'IN(cube{0},box2) AND ~IN(cube{1},box1)'.format(str(i), str(i)))
        # output = return_world()
        if i % 1 == 0:
            runtime = time.time() - start
            print('Run {0}: Worlds - {1}, Computation time - {2}'.format(str(i), str(len(DEL.worlds)), str(runtime)))


if __name__ == '__main__':
    experiment(30)
