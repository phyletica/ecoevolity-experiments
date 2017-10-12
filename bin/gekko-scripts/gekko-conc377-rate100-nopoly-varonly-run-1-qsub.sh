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

prefix=../../gekko-output/run-1

ecoevolity --seed 220053397 --prefix ../../gekko-output/run-1 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc377-rate100-nopoly-varonly.yml 1>../../gekko-output/run-1-gekko-conc377-rate100-nopoly-varonly.out 2>&1