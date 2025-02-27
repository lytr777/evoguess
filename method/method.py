from .models import Estimation
from .instance.models.var import Backdoor


class Method:
    name = 'Method'

    def __init__(self, **kwargs):
        self.cache = {}
        self.kwargs = kwargs
        self.output = kwargs['output']
        self.concurrency = kwargs['concurrency']
        self.can_cache = kwargs.get('can_cache', True)

        try:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()
            self.size = self.comm.Get_size()
        except ModuleNotFoundError:
            self.rank, self.size = 0, 1

    def switch(self, population):
        pass

    def run(self, backdoor: Backdoor, **kwargs) -> Estimation:
        raise NotImplementedError

    def estimate(self, backdoor: Backdoor, **kwargs) -> Estimation:
        key = str(backdoor)
        self.output.st_timer('Estimate_%s' % hash(backdoor), 'estimate')
        if self.can_cache and key in self.cache:
            estimation = self.cache[key]
            estimation.from_cache = True
            self.log_cached(backdoor, estimation.value)
        else:
            estimation = self.run(backdoor, **kwargs)
            self.cache[key] = estimation
        self.output.ed_timer('Estimate_%s' % hash(backdoor))
        return estimation

    def log_run(self, backdoor, count):
        self.output.log('Run method on backdoor: %s' % backdoor, 'With %d cases:' % count)

    def log_cached(self, backdoor, value):
        self.output.log('Hashed backdoor: %s' % backdoor, 'With value: %.7g\n' % value)

    def log_end(self, cases, info, time):
        self.output.log(*list(map(str, cases)))
        self.output.log(str(info))
        self.output.log('Spent time: %.2f s' % time, 'End with value: %.7g' % info.value)

    def __str__(self):
        return '\n'.join(map(str, [
            self.name,
            self.concurrency,
            self.kwargs['instance'],
        ]))


__all__ = [
    'Method',
    'Backdoor',
    'Estimation'
]
