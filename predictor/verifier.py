from .concurrency.models import Task
from .instance.instance import Instance
from .instance.models.var import Backdoor

from copy import copy
from time import time as now


class Verifier:
    name = 'Verifier'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.output = kwargs['output']
        self.chunk_size = kwargs['chunk_size']
        self.concurrency = kwargs['concurrency']

        self.output.log('\n'.join('-- ' + s for s in str(self).split('\n')))
        self.output.log('------------------------------------------------------')

    def __get_next_values(self, values):
        new_values, i = copy(values), len(values) - 1
        while i >= 0 and new_values[i] != 0:
            new_values[i] = 0
            i -= 1

        if i < 0:
            return None
        else:
            new_values[i] = 1
            return new_values

    def verify(self, instance: Instance, backdoor: Backdoor, **kwargs) -> int:
        timestamp, i = now(), 0
        tasks, time_sum = [], 0.
        values = [0] * len(backdoor)
        variables = backdoor.snapshot()

        self.output.log('Run verifier on backdoor: %s' % backdoor,
                        'With %d cases:' % 2 ** len(backdoor))
        while values is not None:
            while values is not None and len(tasks) < self.chunk_size:
                assumption = [x if values[i] else -x for i, x in enumerate(variables)]
                tasks.append(Task(i, bd=assumption, **kwargs))
                values = self.__get_next_values(values)

            if len(tasks) > 0:
                self.output.debug(1, 0, 'Solving...')
                results = self.concurrency.solve(tasks, instance=instance, **self.kwargs)
                for result in results:
                    self.output.log(str(result))
                    time_sum += result.time

                tasks = []

        self.output.log('Spent time: %.2f s' % (now() - timestamp))
        self.output.log('End verifying with value: %.7g' % time_sum)
        self.output.log('------------------------------------------------------')

        return time_sum

    def __str__(self):
        return '\n'.join(map(str, [
            self.name,
            self.concurrency,
        ]))