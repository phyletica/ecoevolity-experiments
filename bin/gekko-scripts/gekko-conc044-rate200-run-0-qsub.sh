#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=40:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../gekko-output/run-0

ecoevolity --seed 698561855 --prefix ../../gekko-output/run-0 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc044-rate200.yml 1>../../gekko-output/run-0-gekko-conc044-rate200.out 2>&1
