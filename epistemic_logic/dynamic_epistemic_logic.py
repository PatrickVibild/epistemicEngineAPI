import copy

from epistemic_logic.predicates.knows import Knows
from epistemic_logic.predicates.predicate import Predicate, NoPredicate
from mlsolver.kripke import World


class DEL:
    world_nr = 0
    current_world = None
    relations = {}
    agents = []
    worlds = []
    vision = {}

    @staticmethod
    def assign_and_increment_worldnr() -> int:
        nr = DEL.world_nr
        DEL.world_nr += 1
        return nr

    @staticmethod
    def new_world(assignment=None) -> World:
        if assignment is None:
            assignment = {}
        world = World(DEL.world_nr, assignment)
        DEL.world_nr += 1
        return world

    @staticmethod
    def reset():
        DEL.world_nr = 0
        DEL.current_world = None
        DEL.relations = {}
        DEL.agents = []
        DEL.worlds = []
        DEL.vision = {}

    @staticmethod
    def update_vision(vision):
        for agent in vision:
            agent[0] = agent[0].upper()
            agent[1] = agent[1].upper()
            DEL.initialize_agents(agent[0])
            DEL.initialize_agents(agent[1])
            if not (agent[1] in DEL.vision[agent[0]]):
                DEL.vision[agent[0]].append(agent[1])

    @staticmethod
    def remove_vision(vision):
        for agent in vision:
            agent[0] = agent[0].upper()
            agent[1] = agent[1].upper()
            if not (agent[0] in DEL.vision):
                raise ValueError('Agent: ' + agent[0] + ' not in database.')
            if not (agent[1] in DEL.vision[agent[0]]):
                continue
            DEL.vision[agent[0]].remove(agent[1])

    @staticmethod
    def update(agent, event):
        event.strip()
        predicates = []
        if 'AND' in event:
            predicates_str = event.split('AND')
            for predicate_str in predicates_str:
                predicate_str.strip()
                if predicate_str[0] == '~':
                    predicates.append(NoPredicate(predicate_str[1:]))
                else:
                    predicates.append(Predicate(predicate_str))
        else:
            if event[0] == '~':
                predicates.append(NoPredicate(event[1:]))
            else:
                predicates.append(Predicate(event))
        # Generating First world ever.
        if DEL.current_world is None:
            DEL.current_world = DEL.new_world(predicates)
            DEL.worlds.append(DEL.current_world)
            # create relations for all agents that sees Agent. From currentWorld to currentWorld
            agents_percept = DEL.agents_sees(agent)
            for a in agents_percept:
                smt = DEL.relations[a]
                smt.add((DEL.current_world.name, DEL.current_world.name))
        # Generating next worlds.
        else:
            # Check if all agents has vision to current a
            # This case we add to all worlds the event.
            if DEL.all_agents_sees(agent):
                for world in DEL.worlds:
                    world.update_world(predicates)
            else:
                # Else we make a product of current worlds.
                '''
                Basic idea for product.
                1. Copy existing worlds
                1.1 New copy world add new event.
                1.2 New current world, is the copy of current world.
                2. For each copy, connect them to original world, and the relations are the reflections on each of the nodes.
                3. for the copied world, remove any relation for agent that dont observe new event.
                4. connect nodes to copies of their nodes.
                4. TODO missing to evaluate pre-conditions of actions to prevent inconsistencies.
                '''
                agents_sees_event = DEL.agents_sees(agent)
                copied_worlds = []
                copied_worlds_name = []
                copied_mapping = {}
                copied_mapping_to_from = {}
                for world in DEL.worlds:
                    # 1
                    copy_world = copy.deepcopy(world)
                    if DEL.current_world == world:
                        DEL.current_world = copy_world
                    copy_world.rename(DEL.assign_and_increment_worldnr())
                    copy_world.update_world(predicates)
                    # 2

                    for agent_relations in DEL.relations:
                        # making a copy to iterate since we gonna add objects to the iterated sets.
                        for relation in DEL.relations[agent_relations].copy():
                            # reflection and copied world.
                            # TODO might be wrong this relation.
                            if relation[1] == relation[0] and relation[1] == copy_world.copy_of:
                                if not (agent_relations in agents_sees_event):
                                    DEL.relations[agent_relations].add((copy_world.name, copy_world.copy_of))
                                else:
                                    DEL.relations[agent_relations].add((copy_world.name, copy_world.name))
                    copied_worlds.append(copy_world)
                    copied_worlds_name.append(copy_world.name)
                    copied_mapping.update({copy_world.name: copy_world.copy_of})
                    copied_mapping_to_from.update({copy_world.copy_of: copy_world.name})
                # 3
                # making copy of relations since relations are been removed when iterated.
                for agent_relations in DEL.relations.copy():
                    if agents_sees_event.__contains__(agent_relations):
                        continue  # do not remove relations for agents who sees the event.
                    for relation in DEL.relations[agent_relations].copy():
                        if copied_worlds_name.__contains__(relation[1]) \
                                and copied_worlds_name.__contains__(relation[0]):
                            DEL.relations[agent_relations].remove(relation)
                # 4
                # copying again the set since we modify the size.
                for agent_relations in DEL.relations.copy():
                    for relation in DEL.relations[agent_relations].copy():
                        # checking for relation in old world, and not reflexives,
                        if (relation[1] != relation[0]) and (not copied_worlds_name.__contains__(relation[1])) \
                                and (not copied_worlds_name.__contains__(relation[0])):
                            DEL.relations[agent_relations].add((
                                copied_mapping_to_from[relation[0]],
                                copied_mapping_to_from[relation[1]]
                            ))
                # Last we add new worlds to DEL worlds.
                DEL.worlds.extend(copied_worlds)

    @staticmethod
    def all_agents_sees(target_agent) -> bool:
        if len(DEL.agents_sees(target_agent)) == len(DEL.agents):
            return True
        return False

    @staticmethod
    def agents_sees(target_agent):
        # agents always see the self's
        have_vision = [target_agent]
        for agent in DEL.agents:
            if DEL.vision[agent].__contains__(target_agent):
                have_vision.append(agent)
        return have_vision

    @staticmethod
    def initialize_agents(agent):
        if not (agent in DEL.agents):
            DEL.agents.append(agent)

        if not (agent in DEL.vision):
            DEL.vision[agent] = []

        if not (agent in DEL.relations):
            DEL.relations[agent] = set()

    @staticmethod
    def crunch_worlds():
        # FIXME brute forced solution. Might be better to implement some data structure.
        for world in DEL.worlds.copy():
            if len(world.assignment) == 0:
                # extend relations. a->b and b->c if b deleted then a->c
                for agent in DEL.relations.copy():
                    for relation in DEL.relations[agent].copy():
                        if relation[1] == world.name:
                            for direction in DEL.relations[agent].copy():
                                if direction[0] == world.name and direction[0] != relation[1]:
                                    DEL.relations[agent].add(
                                        (relation[0], relation[1])
                                    )
                # delete world
                DEL.worlds.remove(world)
                # clean relations
                for agent in DEL.relations.copy():
                    for relation in DEL.relations[agent].copy():
                        if relation[1] == world.name or relation[0] == world.name:
                            DEL.relations[agent].remove(relation)

    @staticmethod
    def world_dictionary():
        worlds = {}
        for world in DEL.worlds:
            worlds[world.name] = world.assignment
        return worlds

    # FIXME holy potato of for loops!
    @staticmethod
    def knowledge(deep):
        worlds = DEL.world_dictionary()
        k = []
        from_reference = DEL.current_world.name
        for agent in DEL.relations:
            lasts = []
            for relation in DEL.relations[agent]:
                if relation[0] == from_reference:
                    agent_knowledge = Knows(agent, worlds[relation[1]], relation[1])
                    k.append(agent_knowledge)
                    lasts.append(agent_knowledge)
            for i in range(deep):
                new_last = []
                for last_k in lasts:
                    for target_agent in DEL.relations:
                        if last_k.agent == target_agent:
                            continue
                        for relation in DEL.relations[target_agent]:
                            if last_k.pointing_w == relation[0]:
                                tmp = Knows(target_agent, worlds[relation[1]], relation[1])
                                last_k.add_next_knowledge(tmp)
                                new_last.append(tmp)
                lasts = new_last
        return k



