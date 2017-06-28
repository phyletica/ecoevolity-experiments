#! /bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=10:00:00
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

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

scriptpath="$(basename "$0")"
scriptfile="${scriptpath##*/}"
scriptname="${scriptfile%.*}"
siminfo="${scriptname/simcoevolity-val-/}"
rngseed="${siminfo##*-}"
siminfo="${siminfo%-*}"
nreps="${siminfo##*-}"
siminfo="${siminfo%-*}"
batch="${siminfo##*-}"
simname="${siminfo%-*}"
locusinfo="${simname##*-}"
configname="${simname%-*}"

locusflag=""
if [ "$locusinfo" == "l0100" ] 
then
    locusflag="-l 100"
elif [ "$locusinfo" == "l0500" ] 
then
    locusflag="-l 500"
elif [ "$locusinfo" == "l1000" ] 
then
    locusflag="-l 1000"
elif [ "$locusinfo" == "l0001" ] 
then
    locusflag=""
else
    echo "ERROR: Unrecognized locus flag: ${locusinfo}"
    exit 1
fi

cfgpath="../configs/config-${configname}.yml"
outputdir="../simulations/validation/${simname}/${batch}"
stdoutpath="${scriptfile}.out"

mkdir -p "$outputdir"

simcoevolity --seed="$rngseed" -n "$nreps" "$locusflag" -o "$outputdir" "$cfgpath" 1>"${stdoutpath}" 2>&1
