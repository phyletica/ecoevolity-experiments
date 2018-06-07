#! /bin/bash

burnin=201

eco_dir="../analyses/ecoevolity"
output_dir="../results"
if [ ! -d "$output_dir" ]
then
    mkdir -p "$output_dir"
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

labels='-l "BabuyanClaro0" "Babuyan Claro" -l "Calayan0" "Calayan" -l "MaestreDeCampo1" "Maestre De Campo" -l "Masbate1" "Masbate" -l "CamiguinNorte2" "Camiguin Norte" -l "Dalupiri2" "Dalupiri" -l "root-BabuyanClaro0" "Babuyan Claro-Calayan Root" -l "root-MaestreDeCampo1" "Maestre De Campo-Masbate Root" -l "root-CamiguinNorte2" "Camiguin Norte-Dalupiri Root"'

convert_labels_to_array $labels

gzip -f -d -k ${eco_dir}/*state*log.gz

pyco-sumtimes -f --x-limits 0.0 0.008 -x "Divergence time" -y "" -b "$burnin" "${label_array[@]}" -p "${output_dir}/" ${eco_dir}/*state*log.gz
sumcoevolity -f -b $burnin -n 1000000 -p "${output_dir}/" -c "../configs/ecoevolity-config.yml" ${eco_dir}/*state*log
pyco-sumevents -p "${output_dir}/" -f --no-legend "${output_dir}/sumcoevolity-results-nevents.txt"
