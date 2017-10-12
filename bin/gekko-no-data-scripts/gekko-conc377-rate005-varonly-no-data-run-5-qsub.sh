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

ecoevolity --seed 798463030 --prefix ../../gekko-output/no-data-run-5 --ignore-data --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc377-rate005-varonly.yml 1>../../gekko-output/no-data-run-5-gekko-conc377-rate005-varonly.out 2>&1