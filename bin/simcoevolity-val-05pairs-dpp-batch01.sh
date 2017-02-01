#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:30:00
#PBS -j oe 
#   #PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

CFGPATH="../configs/config-5pairs-dpp.yml"
OUTPUTDIR="../simulations/validation/05pairs-dpp/batch01"
SEED="63415263"

mkdir -p "$OUTPUTDIR"

simcoevolity --seed="$SEED" -n 100 -o "$OUTPUTDIR" "$CFGPATH"
