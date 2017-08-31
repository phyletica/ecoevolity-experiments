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

prefix=../gekko-output/run-8

ecoevolity --seed 161687824 --prefix ../gekko-output/run-8 --relax-missing-sites --relax-constant-sites ../configs/gekkocontrol-nopoly.yml 1>../gekko-output/run-8-gekkocontrol-nopoly.out 2>&1
