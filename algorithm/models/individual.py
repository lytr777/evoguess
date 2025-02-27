from numpy import sign
from typing import List

from method.instance.models.var import Backdoor


class Individual:
    def __init__(self, backdoor: Backdoor):
        self.backdoor = backdoor
        self.value = float('inf')

    def set(self, value):
        self.value = value
        return self

    def compare(self, other):
        try:
            vs = int(sign(self.value - other.value))
        except ValueError:
            vs = 0

        return vs or len(other) - len(self)

    def __len__(self):
        return len(self.backdoor)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __eq__(self, other):
        return self.compare(other) == 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __str__(self):
        return '%s by %.7g' % (self.backdoor, self.value)


Population = List[Individual]

__all__ = [
    'Individual',
    'Population'
]
