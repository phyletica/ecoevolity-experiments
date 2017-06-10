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
    s = ("#PBS -l nodes=1:ppn=1\n"
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

def write_qsub(config_path,
        restrict_nodes = False,
        walltime = "5:00:00",
        no_pbs = False,
        rng = _RNG):
    qsub_prefix = os.path.splitext(config_path)[0]
    qsub_path = qsub_prefix + "-qsub.sh"
    if os.path.exists(qsub_path):
        return
    seed = rng.randint(1, 999999999)
    with open(qsub_path, 'w') as out:
        if not no_pbs:
            out.write(get_pbs_header(restrict_nodes, walltime))
        out.write("ecoevolity --seed {0} --relax-constant-sites {1}\n".format(
            seed,
            os.path.basename(config_path)))

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
    parser.add_argument('--walltime',
            action = 'store',
            type = str,
            default = '5:00:00',
            help = 'Walltime for qsub scripts.')
    parser.add_argument('--restrict-nodes',
            action = 'store_true',
            help = 'Run only on lab nodes.')
    parser.add_argument('--no-pbs',
            action = 'store_true',
            help = 'No PBS preamble.')

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)
    if not args.seed:
        args.seed = random.randint(1, 999999999)
    _RNG.seed(args.seed)

    config_path_pattern = os.path.join(project_util.VAL_DIR, "*", "*", "simcoevolity-sim-*.yml") 

    for config_path in glob.glob(config_path_pattern):
        write_qsub(config_path = config_path,
                restrict_nodes = args.restrict_nodes,
                walltime = args.walltime,
                no_pbs = args.no_pbs)
    

if __name__ == "__main__":
    main_cli()
