#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

prefix=../../gekko-output/no-data-run-5

ecoevolity --seed 21423970 --prefix ../../gekko-output/no-data-run-5 --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc044-rate100-nopoly-varonly.yml 1>../../gekko-output/no-data-run-5-gekko-conc044-rate100-nopoly-varonly.out 2>&1
