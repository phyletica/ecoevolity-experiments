#!/bin/bash

current_dir="$(pwd)"

project_dir="$(./project_util.py)"
gekko_output_dir="${project_dir}/gekko-output"
cd "$gekko_output_dir"

for conc in "044" "377"
do
    for rate in "005" "010" "020" "100" "200"
    do
        for suffix in "-" "-nopoly-"
        do
            echo "pyco-sumchains run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log"
            pyco-sumchains run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log 1>pyco-sumchains-conc${conc}-rate${rate}${suffix}table.txt 2>pyco-sumchains-conc${conc}-rate${rate}${suffix}stderr.txt
        done
    done
done

for conc in "044" "377"
do
    for rate in "002" "005" "010" "020" "100"
    do
        for suffix in "-varonly-" "-nopoly-varonly-"
        do
            echo "pyco-sumchains run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log"
            pyco-sumchains run-?-gekko-conc${conc}-rate${rate}${suffix}state-run-1.log 1>pyco-sumchains-conc${conc}-rate${rate}${suffix}table.txt 2>pyco-sumchains-conc${conc}-rate${rate}${suffix}stderr.txt
        done
    done
done

cd "$current_dir"
