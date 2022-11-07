import collections


class Predicate:
    def __init__(self, predicate_str: str):
        predicate_str = predicate_str.strip()
        values = predicate_str.split('(')
        functor = values[0]
        if values[1][-1] != ')':
            raise ValueError('input predicate ' + predicate_str + 'wrong format')
        args_str = values[1][:-1]
        args = list()
        for argument in args_str.split(','):
            args.append(argument.strip())
        self.functor = functor
        self.args = args

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.functor == other.functor and \
               collections.Counter(self.args) == collections.Counter(other.args)

    def __str__(self):
        return '{}({})'.format(self.functor, ', '.join(self.args))

    def is_negation(self, other):
        if not isinstance(other, NoPredicate):
            return False
        return self.functor == other.functor and \
               collections.Counter(self.args) == collections.Counter(other.args)

    def negate(self):
        return NoPredicate(str(self))


class NoPredicate(Predicate):
    def __int__(self, predicate_str: str):
        super(predicate_str)

    def __str__(self):
        return '~{}({})'.format(self.functor, ', '.join(self.args))

    def __eq__(self, other):
        if not isinstance(other, NoPredicate):
            return False
        return self.functor == other.functor and \
               collections.Counter(self.args) == collections.Counter(other.args)

    def is_negation(self, other):
        if not isinstance(other, Predicate):
            return False
        return self.functor == other.functor and \
               collections.Counter(self.args) == collections.Counter(other.args)

    def negate(self):
        return Predicate(str(self)[1:])
