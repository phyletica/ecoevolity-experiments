#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=10:00:00
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

myhost="$(hostname | tr -d '0123456789')"
if [ "$myhost" == "uv" ] || [ "$myhost" == "dmc" ]
then
    module load gcc/6.1.0
fi

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

simname="03pairs-rj-root-1000"
cfgpath="../configs/config-${simname}.yml"
outputdir="../simulations/validation/${simname}/batch01"
rngseed="12312"
nreps=1000

mkdir -p "$outputdir"

simcoevolity --seed="$rngseed" -n "$nreps" -o "$outputdir" "$cfgpath"
