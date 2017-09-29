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

prefix=../gekko-output/no-data-run-8

ecoevolity --seed 161687824 --prefix ../gekko-output/no-data-run-8 --ignore-data --relax-missing-sites --relax-constant-sites ../configs/gekkocontrol-varonly.yml 1>../gekko-output/no-data-run-8-gekkocontrol-varonly.out 2>&1
