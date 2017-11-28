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

locussize="100"
simname="03pairs-dpp-root-0100-100k"
cfgpath="../configs/config-${simname}.yml"
outputdir="../simulations/validation/${simname}-0100ul/batch005"
rngseed=492178337
nreps=100

mkdir -p "$outputdir"

simcoevolity --max-one-variable-site-per-locus --seed="$rngseed" -n "$nreps" -l "$locussize" -o "$outputdir" "$cfgpath"