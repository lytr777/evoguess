from ..strategy import *

import warnings
from math import ceil


class Elitism(Strategy):
    def __init__(self, **kwargs):
        self.elites = kwargs['mu']
        self.popsize = kwargs['lmbda']
        self.crossover = kwargs['crossover']
        self.mobs = self.popsize - self.elites
        super().__init__(self.popsize, **kwargs)
        self.name = 'Strategy: Elitism (%d over %d)' % (self.elites, self.popsize)
        if self.mobs % 2 != 0:
            warnings.warn('mob\'s count should be even, but equals %d' % self.mobs, UserWarning)

    def tweak(self, generator: Iterable[Individual]) -> Tuple[Population, Population]:
        j, size = 0, ceil(self.mobs / 2.) * 2
        parents = [next(generator) for _ in range(size)]

        children = []
        while j < len(parents):
            i1, i2 = parents[j], parents[j + 1]
            crossed = self.crossover.cross(i1, i2)
            mutated = map(self.mutation.mutate, crossed)
            children.extend(mutated)
            j += 2

        return parents[:self.elites], children[:self.mobs]

    def configure(self, limits):
        return [
            *super().configure(limits),
            self.crossover.configure(limits)
        ]

    def __len__(self):
        return self.popsize

    def __str__(self):
        return '\n'.join(map(str, [
            super().__str__(),
            self.crossover
        ]))


__all__ = ['Elitism']
