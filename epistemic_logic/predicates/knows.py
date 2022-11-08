from epistemic_logic.predicates.predicate import Predicate


class Knows:
    def __init__(self, agent, info, pointing_w):
        self.agent = agent
        self.info = info
        self.pointing_w = pointing_w
        self.ref_knowledge = []

    def add_next_knowledge(self, k):
        self.ref_knowledge.append(k)

    def __str__(self):
        infos_str = [str(i) for i in self.info]
        return 'K_{}({})'.format(self.agent, ' AND '.join(infos_str))

    def stringify(self):
        '''
        creates recursively knowledge of the state of worlds and beliefs of other agents.
        '''
        if len(self.ref_knowledge) > 0:
            current_k = self.__str__()
            tmp = []
            for k in self.ref_knowledge:
                k_values = k.stringify()
                for i in k_values:
                    k_string = 'K_{}({})'.format(self.agent, i)
                    tmp.append(k_string)
            output = [current_k]
            output.extend(tmp)
            return output
        return [self.__str__()]
