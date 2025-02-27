import argparse
import subprocess

from datetime import datetime as dt

today = dt.today()
z = lambda n: ('0%s' if n <= 9 else '%s') % n

date = '%s.%s.%s' % (today.year, z(today.month), z(today.day))
time = '%s:%s:%s' % (z(today.hour), z(today.minute), z(today.second))
now = '%s_%s' % (date, time)

parser = argparse.ArgumentParser(description='Configurator')
parser.add_argument('instance', type=str, help='instance of problem')
parser.add_argument('-f', '--function', type=str, default='', help='estimation function')
parser.add_argument('-file', type=str, default='', help='additional file')

parser.add_argument('-nodes', '--nodes', metavar='5', type=int, default=5, help='nodes')
parser.add_argument('-native', '--native', metavar='str', type=str, default='', help='native script')
parser.add_argument('-script', '--script', metavar='main', type=str, default='', help='script')
parser.add_argument('-sector', '--sector', metavar='intel', type=str, default='intel', help='sector')

parser.add_argument('-t', '--threads', metavar='1', type=int, default=1, help='concurrency threads')
parser.add_argument('-d', '--description', metavar='str', type=str, default='', help='launch description')
parser.add_argument('-wt', '--walltime', metavar='hh:mm:ss', type=str, default='24:00:00', help='wall time')
parser.add_argument('-v', '--verbosity', metavar='3', type=int, default=3, help='debug [0-3] verbosity level')
parser.add_argument('-i', '--incremental', action='store_true', help='incremental mode')
parser.add_argument('-dall', '--debug_all', action='store_true', help='debug on all nodes')

parser.add_argument('-s', '--solver', metavar='str', type=str, default='g3', help='SAT-solver to solve')
parser.add_argument('-pr', '--propagator', metavar='str', type=str, default='', help='SAT-solver to propagate')

parser.add_argument('-a', '--algorithm', metavar='str', type=str, default='', help='optimization algorithm')
parser.add_argument('-tl', metavar='0', type=int, default=0, help='time limit for ibs')
parser.add_argument('-r', '--repeats', metavar='0', type=int, default=0, help='repeats count')
parser.add_argument('-n', '--sampling', metavar='0', type=int, default=0, help='estimation sampling')
parser.add_argument('-sn', '--step_size', metavar='0', type=int, default=0, help='stat test step size')
parser.add_argument('-st', '--stagnation', metavar='0', type=int, default=0, help='stagnation limit')
parser.add_argument('-o', '--order', action='store_true', help='use nobs order')

args = parser.parse_args()

with open('%s.qsub' % now, 'w+') as f:
    if len(args.native) > 0:
        name = 'native:%s' % args.instance
    else:
        name = '%s:%s' % (args.script, args.instance)

    f.write('#!/bin/bash\n')
    f.write('#\n')
    f.write('#PBS -N %s\n' % name)
    f.write('#PBS -l nodes=%d' % args.nodes)
    f.write(':%s' % args.sector)
    s_threads = {
        'amd': 32,
        'intel': 36
    }[args.sector] or 32
    f.write(':ppn=%d' % s_threads)
    wts = [int(w) for w in args.walltime.split(':')]
    wts[0] += 1
    f.write(',walltime=%s\n' % ':'.join(map(str, map(z, wts))))
    f.write('#PBS -m n\n\n')
    f.write('source /share/apps/intel/iccvars.sh intel64\n')
    f.write('source /share/apps/intel/mpivars.sh\n')
    f.write('export LD_LIBRARY_PATH=/share/apps/gcc/7.3/lib64:$LD_LIBRARY_PATH\n')
    f.write('export I_MPI_EAGER_THRESHOLD=128000\n\n')
    f.write('cd $PBS_O_WORKDIR\n')
    script_sh = '%s.sh' % now
    f.write('/share/apps/bin/mpiexec -n %d -perhost 1 ./%s\n' % (args.nodes, script_sh))

with open('%s.sh' % now, 'w+') as f:
    f.write('#!/bin/bash\n\n')

    if len(args.native) > 0:
        if len(args.script) > 0:
            f.write('python3 %s.py ' % args.script)
        f.write(args.native)
    else:
        f.write('python3 %s.py' % args.script)
        f.write(' %s' % args.instance)
        if len(args.function) > 0:
            f.write(' %s' % args.function)
        if len(args.file) > 0:
            f.write(' %s' % args.file)

        f.write(' -t %d' % args.threads)
        f.write(' -d \"%s\"' % args.description)
        f.write(' -wt %s' % args.walltime)
        f.write(' -v %d' % args.verbosity)
        if args.incremental: f.write(' -i')
        if args.debug_all: f.write(' -dall')

        f.write(' -s %s' % args.solver)
        if len(args.propagator) > 0: f.write(' -pr %s' % args.propagator)

        if len(args.algorithm) > 0: f.write(' -a %s' % args.algorithm)
        if args.tl > 0: f.write(' -tl %d' % args.tl)
        if args.repeats > 0: f.write(' -r %d' % args.repeats)
        if args.sampling > 0: f.write(' -n %d' % args.sampling)
        if args.step_size > 0: f.write(' -sn %d' % args.step_size)
        if args.stagnation > 0: f.write(' -st %d' % args.stagnation)
        if args.order: f.write(' -o')

    f.write('\n')


print('chmod +x %s.sh && qsub.%s %s.qsub' % (now, args.sector, now))
