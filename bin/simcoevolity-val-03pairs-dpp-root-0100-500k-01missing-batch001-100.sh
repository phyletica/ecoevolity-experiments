#! /bin/sh

username="$USER"
if [ "$username" == "aubjro" ]
then
    module load gcc/6.1.0
fi

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

simname="03pairs-dpp-root-0100-500k-01missing"
cfgpath="../configs/config-${simname}.yml"
outputdir="../simulations/validation/${simname}/batch001"
rngseed=227187886
nreps=100

mkdir -p "$outputdir"

simcoevolity --relax-missing-sites --seed="$rngseed" -n "$nreps" -o "$outputdir" "$cfgpath"
