#! /usr/bin/env python

import sys
import os
import argparse
import random
import glob
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import project_util

_RNG = random.Random()

def get_pbs_header(restrict_nodes = False, walltime = "5:00:00"):
    s = ("#! /bin/sh\n"
         "#PBS -l nodes=1:ppn=1\n"
         "#PBS -l walltime={0}\n"
         "#PBS -j oe\n".format(walltime))
    if restrict_nodes:
        s += "#PBS -l jobflags=ADVRES:jro0014_lab.56281\n"
    s += ("\n"
          "if [ -n \"$PBS_JOBNAME\" ]\n"
          "then\n"
          "    source \"${PBS_O_HOME}/.bash_profile\"\n"
          "    cd \"$PBS_O_WORKDIR\"\n"
          "    module load gcc/5.3.0\n"
          "fi\n\n")
    return s

def get_asc_header():
    s = ("#! /bin/sh\n\n"
         "username=\"$USER\"\n"
         "if [ \"$username\" == \"aubjro\" ]\n"
         "then\n"
         "    module load gcc/6.1.0\n"
         "fi\n\n")
    return s

def write_qsub(config_path,
        run_number = 1,
        restrict_nodes = False,
        walltime = "2:00:00",
        asc = False,
        rng = _RNG):
    qsub_prefix = os.path.splitext(config_path)[0]
    qsub_path = "{0}-run-{1}-qsub.sh".format(qsub_prefix, run_number)
    if os.path.exists(qsub_path):
        return
    config_file = os.path.basename(config_path)
    stdout_path = "{0}-run-{1}.out".format(config_file, run_number)
    seed = rng.randint(1, 999999999)
    assert(not os.path.exists(qsub_path))
    with open(qsub_path, 'w') as out:
        if asc:
            out.write(get_asc_header())
        else:
            out.write(get_pbs_header(restrict_nodes, walltime))
        out.write("ecoevolity --seed {0} --relax-constant-sites {1} 1>{2} 2>&1\n".format(
                seed,
                config_file,
                stdout_path))

def arg_is_positive_int(i):
    """
    Returns int if argument is a positive integer; returns argparse error
    otherwise.

    >>> arg_is_positive_int(1) == 1
    True
    """

    try:
        if int(i) < 1:
            raise
    except:
        msg = '{0!r} is not a positive integer'.format(i)
        raise argparse.ArgumentTypeError(msg)
    return int(i)


def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--seed',
            action = 'store',
            type = int,
            help = 'Random number seed to use for the analysis.')
    parser.add_argument('--number-of-runs',
            action = 'store',
            type = int,
            default = 2,
            help = 'Number of qsubs to generate per config (Default: 2).')
    parser.add_argument('--walltime',
            action = 'store',
            type = str,
            default = '2:00:00',
            help = 'Walltime for qsub scripts (Default: 2:00:00).')
    parser.add_argument('--restrict-nodes',
            action = 'store_true',
            help = 'Run only on lab nodes.')
    parser.add_argument('--asc',
            action = 'store_true',
            help = 'Format script for AL super computer.')

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)
    if not args.seed:
        args.seed = random.randint(1, 999999999)
    _RNG.seed(args.seed)

    config_path_pattern = os.path.join(project_util.VAL_DIR, "*", "*", "*simcoevolity-sim-*.yml") 
    for config_path in glob.glob(config_path_pattern):
        for i in range(args.number_of_runs):
            write_qsub(config_path = config_path,
                    run_number = i + 1,
                    restrict_nodes = args.restrict_nodes,
                    walltime = args.walltime,
                    asc = args.asc)
    

if __name__ == "__main__":
    main_cli()
