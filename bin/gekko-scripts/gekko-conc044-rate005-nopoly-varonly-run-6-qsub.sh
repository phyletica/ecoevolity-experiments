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

prefix=../../gekko-output/run-6

ecoevolity --seed 420828461 --prefix ../../gekko-output/run-6 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc044-rate005-nopoly-varonly.yml 1>../../gekko-output/run-6-gekko-conc044-rate005-nopoly-varonly.out 2>&1