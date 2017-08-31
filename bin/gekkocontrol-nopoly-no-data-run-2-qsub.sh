#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=5:00:00
#PBS -j oe
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../gekko-output/no-data-run-2

ecoevolity --seed 10169170 --prefix ../gekko-output/no-data-run-2 --ignore-data --relax-missing-sites --relax-constant-sites ../configs/gekkocontrol-nopoly.yml 1>../gekko-output/no-data-run-2-gekkocontrol-nopoly.out 2>&1
