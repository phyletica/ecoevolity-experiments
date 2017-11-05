#!/bin/bash
#PBS -l nodes=1:ppn=1
#PBS -l walltime=1:00:00
#PBS -j oe 

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

label_array=()
convert_labels_to_array() {
    local concat=""
    local t=""
    label_array=()

    for word in $@
    do
        local len=`expr "$word" : '.*"'`

        [ "$len" -eq 1 ] && concat="true"

        if [ "$concat" ]
        then
            t+=" $word"
        else
            word=${word#\"}
            word=${word%\"}
            label_array+=("$word")
        fi

        if [ "$concat" -a "$len" -gt 1 ]
        then
            t=${t# }
            t=${t#\"}
            t=${t%\"}
            label_array+=("$t")
            t=""
            concat=""
        fi
    done
}

burnin=201

current_dir="$(pwd)"

project_dir="$(./project_util.py)"
gekko_output_dir="${project_dir}/gekko-output"
cd "$gekko_output_dir"

plot_dir="../gekko-results"
mkdir -p "$plot_dir"

labels='-l "BabuyanClaro8" "Babuyan Claro" -l "Calayan8" "Calayan" -l "Lubang10" "Lubang" -l "Luzon10" "Luzon" -l "MaestreDeCampo11" "Maestre De Campo" -l "Masbate11" "Masbate" -l "CamiguinNorte15" "Camiguin Norte" -l "Dalupiri15" "Dalupiri" -l "root-BabuyanClaro8" "Babuyan Claro-Calayan Root" -l "root-Lubang10" "Lubang-Luzon Root" -l "root-MaestreDeCampo11" "Maestre De Campo-Masbate Root" -l "root-CamiguinNorte15" "Camiguin Norte-Dalupiri Root"'

convert_labels_to_array $labels

for conc in "044" "377"
do
    for rate in "005" "010" "020" "100" "200"
    do
        for suffix in "" "-nopoly"
        do
            pyco-sumtimes -f -z -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            pyco-sumsizes -f -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-" -c "../configs/gekko-conc${conc}-rate${rate}${suffix}.yml" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            pyco-sumevents -p "${plot_dir}/pyco-sumevents-conc${conc}-rate${rate}${suffix}-" -f --no-legend "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-sumcoevolity-results-nevents.txt"
        done
    done
done

for conc in "044" "377"
do
    for rate in "002" "005" "010" "020" "100"
    do
        for suffix in "-varonly" "-nopoly-varonly"
        do
            pyco-sumtimes -f -z -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumtimes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            pyco-sumsizes -f -x "" -y "" -b $burnin "${label_array[@]}" -p "${plot_dir}/pyco-sumsizes-conc${conc}-rate${rate}${suffix}-" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            sumcoevolity -b $burnin -n 1000000 -p "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-" -c "../configs/gekko-conc${conc}-rate${rate}${suffix}.yml" run-?-gekko-conc${conc}-rate${rate}${suffix}-state-run-1.log
            pyco-sumevents -p "${plot_dir}/pyco-sumevents-conc${conc}-rate${rate}${suffix}-" -f --no-legend "${plot_dir}/sumcoevolity-conc${conc}-rate${rate}${suffix}-sumcoevolity-results-nevents.txt"
        done
    done
done

cd "$current_dir"
