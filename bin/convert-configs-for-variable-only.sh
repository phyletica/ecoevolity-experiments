#! /bin/sh
#PBS -l nodes=1:ppn=1
#PBS -l walltime=10:00:00
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

for config_path in ../simulations/validation/*/batch*/*config.yml
do
    dir_name="$(dirname $config_path)"
    base_name="$(basename $config_path)"
    new_config_name="var-only-${base_name}"
    new_config_path="${dir_name}/${new_config_name}"

    sed -e "s/constant_sites_removed: false/constant_sites_removed: true/g" "$config_path" > "$new_config_path"
done
