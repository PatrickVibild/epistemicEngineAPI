import copy

from epistemic_logic.predicates.predicate import *


class World:
    """
    Represents the nodes of Kripke and it extends the graph to Kripke
    Structure by assigning a subset of propositional variables to each world.
    """

    def __init__(self, name, assignment):
        self.name = name
        self.assignment = assignment
        self.copy_of = None
        self.child_name = None

    def __eq__(self, other):
        return self.name == other.name and self.assignment == other.assignment

    def __str__(self):
        return "(" + self.name + ',' + str(self.assignment) + ')'

    def rename(self, name):
        self.copy_of = self.name
        self.name = name

    def update_world(self, predicates):
        for predicate in predicates:
            if isinstance(predicate, NoPredicate):
                negated = predicate.negate()
                if negated in self.assignment:
                    self.assignment.remove(negated)
            else:
                if not (predicate in self.assignment):
                    self.assignment.append(predicate)

    def create_child(self, name, predicates):
        child = copy.deepcopy(self)
        child.rename(name)
        self.child_name = child.name
        child.update_world(predicates)
        return child


