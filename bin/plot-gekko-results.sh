#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe 

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

burnin=201

current_dir="$(pwd)"

project_dir="$(./project_util.py)"
gekko_output_dir="${project_dir}/gekko-output"
cd "$gekko_output_dir"

plot_dir="../gekko-results"
mkdir -p "$plot_dir"

for conc in "044" "377"
do
    for rate in "005" "010" "020" "100" "200"
    do
        for suffix in "-" "-nopoly-"
        do
            pyco-sumtimes -f -z -b $burnin -p "${plot_dir}/pyco-sumtimes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
            pyco-sumsizes -f -b $burnin -p "${plot_dir}/pyco-sumsizes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
            sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-" -c "../configs/gekko-conc${conc}-rate${rate}${suffix}.yml" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
        done
    done
done

for conc in "044" "377"
do
    for rate in "002" "005" "010" "020" "100"
    do
        for suffix in "-varonly-" "-nopoly-varonly-"
        do
            pyco-sumtimes -f -z -b $burnin -p "${plot_dir}/pyco-sumtimes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
            pyco-sumsizes -f -b $burnin -p "${plot_dir}/pyco-sumsizes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
            sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-" -c "../configs/gekko-conc${conc}-rate${rate}${suffix}.yml" run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log
        done
    done
done

cd "$current_dir"
