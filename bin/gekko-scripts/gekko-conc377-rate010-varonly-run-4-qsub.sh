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

prefix=../../gekko-output/run-4

ecoevolity --seed 67705979 --prefix ../../gekko-output/run-4 --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../../configs/gekko-conc377-rate010-varonly.yml 1>../../gekko-output/run-4-gekko-conc377-rate010-varonly.out 2>&1