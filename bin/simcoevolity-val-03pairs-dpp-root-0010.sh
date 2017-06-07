#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=02:00:00
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    echo ------------------------------------------------------
    echo -n 'Job is running on node '; cat $PBS_NODEFILE
    echo ------------------------------------------------------
    echo PBS: qsub is running on $PBS_O_HOST
    echo PBS: originating queue is $PBS_O_QUEUE
    echo PBS: executing queue is $PBS_QUEUE
    echo PBS: working directory is $PBS_O_WORKDIR
    echo PBS: execution mode is $PBS_ENVIRONMENT
    echo PBS: job identifier is $PBS_JOBID
    echo PBS: job name is $PBS_JOBNAME
    echo PBS: node file is $PBS_NODEFILE
    echo PBS: current home directory is $PBS_O_HOME
    echo PBS: PATH = $PBS_O_PATH
    echo ------------------------------------------------------

    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

CFGPATH="../configs/config-03pairs-dpp-root-0010.yml"
OUTPUTDIR="../simulations/validation/03pairs-dpp-root-0010/batch01"
SEED="27215356"

mkdir -p "$OUTPUTDIR"

simcoevolity --seed="$SEED" -n 100 -o "$OUTPUTDIR" "$CFGPATH"