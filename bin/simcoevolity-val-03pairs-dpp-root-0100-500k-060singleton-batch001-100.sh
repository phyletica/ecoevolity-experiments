#! /bin/sh

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR

    module load gcc/5.3.0
fi

ssprob="0.60"
ssplabel="$(echo $ssprob | sed -e "s/\.//g")singleton"
simname="03pairs-dpp-root-0100-500k"
cfgpath="../configs/config-${simname}.yml"
outputdir="../simulations/validation/${simname}-${ssplabel}/batch001"
rngseed=994741211
nreps=100

mkdir -p "$outputdir"

simcoevolity --seed="$rngseed" --singleton-sample-probability "$ssprob" -n "$nreps" -o "$outputdir" "$cfgpath"
