import copy

from epistemic_logic.predicates.knows import Knows
from epistemic_logic.predicates.predicate import Predicate, NoPredicate
from epistemic_logic.world import World


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
        for agents in vision:
            agents[0] = agents[0].upper()
            agents[1] = agents[1].upper()
            DEL.initialize_agents(agents[0])
            DEL.initialize_agents(agents[1])
            if not (agents[1] in DEL.vision[agents[0]]):
                DEL.vision[agents[0]].append(agents[1])

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
    def update(agent: object, event: object) -> object:
        event = event.strip()
        predicates = []
        if 'AND' in event:
            predicates_str = event.split('AND')
            for predicate_str in predicates_str:
                predicate_str = predicate_str.strip()
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
                1.0 Check if the current world is reference to agents who views the action.
                1.1 New copy world add new event.
                1.2 New current world, is the copy of current world. 
                2. For each copy, connect them to original world, and the relations are the reflections on each of the 
                nodes.
                3. for the copied world, remove any relation for agent that dont observe new event.
                4. connect nodes to copies of their nodes.
                4.1 If we create a new world and there is no reference from that world to its copy, we use reflexion 
                agents in the reference to unify the new and old world. This reference is been deleted afterwards
                when crunching empty or duplicated worlds.
                '''
                agents_sees_event = DEL.agents_sees(agent)
                copied_worlds = []
                copied_worlds_name = []
                copied_mapping = {}
                copied_mapping_to_from = {}
                for world in DEL.worlds:
                    # 1.0
                    agents_knowledge = DEL.knowledge(len(DEL.worlds) + 1)
                    modifiable_world = False
                    for a in agents_sees_event:
                        for a_k in agents_knowledge:
                            if a_k.agent == a and a_k.pointing_w == world.name:
                                modifiable_world = True
                                break
                    # If agent that beliefs in the current world has not seeing the event we skip world.
                    if modifiable_world:
                        world.update_world(predicates)
                        continue

                    # 1
                    child_world = world.create_child(DEL.assign_and_increment_worldnr(), predicates)
                    if DEL.current_world == world:
                        DEL.current_world = child_world
                    # 2
                    for agent_relation in DEL.relations:
                        # making a copy to iterate since we gonna add objects to the iterated sets.
                        for relation in DEL.relations[agent_relation].copy():
                            # reflection and copied world.
                            if relation[1] == relation[0] and relation[1] == child_world.copy_of:
                                if not (agent_relation in agents_sees_event):
                                    DEL.relations[agent_relation].add((child_world.name, child_world.copy_of))
                                else:
                                    DEL.relations[agent_relation].add((child_world.name, child_world.name))

                    copied_worlds.append(child_world)
                    copied_worlds_name.append(child_world.name)
                    copied_mapping.update({child_world.name: child_world.copy_of})
                    copied_mapping_to_from.update({child_world.copy_of: child_world.name})
                # 3
                # making copy of relations since relations are been removed when iterated.
                for agent_relation in DEL.relations.copy():
                    if agents_sees_event.__contains__(agent_relation):
                        continue  # do not remove relations for agents who sees the event.
                    for relation in DEL.relations[agent_relation].copy():
                        if copied_worlds_name.__contains__(relation[1]) \
                                and copied_worlds_name.__contains__(relation[0]):
                            DEL.relations[agent_relation].remove(relation)
                # 4
                # copying again the set since we modify the size.

                for agent_relation in DEL.relations.copy():
                    for relation in DEL.relations[agent_relation].copy():
                        # checking for relation in old world, and not reflexives,
                        if (relation[1] != relation[0]) and (not copied_worlds_name.__contains__(relation[1])) \
                                and (not copied_worlds_name.__contains__(relation[0])):
                            try:
                                DEL.relations[agent_relation].add((
                                    copied_mapping_to_from[relation[0]],
                                    copied_mapping_to_from[relation[1]]
                                ))
                            except:
                                print('ups')

                # Last we add new worlds to DEL worlds.
                DEL.worlds.extend(copied_worlds)
                # now we delete empty worlds and fix relations.
                DEL.crunch_worlds()

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
        '''
        Function that removes empty worlds and pass the relations overs. We skip the current world for crunching.
        '''
        # FIXME brute forced solution. Might be better to implement some data structure.
        for world in DEL.worlds.copy():
            # we skip current world for crunching.
            if len(world.assignment) == 0 and world.name != DEL.current_world.name:
                # extend relations. a->b and b->c if b deleted then a->c
                for agent in DEL.relations.copy():
                    for relation in DEL.relations[agent].copy():
                        if relation[1] == world.name:
                            for direction in DEL.relations[agent].copy():
                                if direction[0] == world.name and direction[0] != relation[1]:
                                    DEL.relations[agent].add(
                                        (relation[0], relation[1])
                                    )
                        if relation[0] == world.name:
                            DEL.relations[agent].add((world.child_name, relation[1]))
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
