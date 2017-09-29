#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=5:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../gekko-output/no-data-run-10

ecoevolity --seed 523597580 --prefix ../gekko-output/no-data-run-10 --ignore-data --relax-missing-sites --relax-constant-sites ../configs/gekkocontrol.yml 1>../gekko-output/no-data-run-10-gekkocontrol.out 2>&1
