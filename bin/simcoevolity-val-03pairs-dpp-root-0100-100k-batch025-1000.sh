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

simname="03pairs-dpp-root-0100-100k"
cfgpath="../configs/config-${simname}.yml"
outputdir="../simulations/validation/${simname}/batch025"
rngseed=747135437
nreps=1000

mkdir -p "$outputdir"

simcoevolity --seed="$rngseed" -n "$nreps" -o "$outputdir" "$cfgpath"
