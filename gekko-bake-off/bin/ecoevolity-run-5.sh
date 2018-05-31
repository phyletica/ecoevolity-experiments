#! /bin/sh

run=5
seed=882041982

if [ -n "$PBS_JOBNAME" ]
then
    source "${PBS_O_HOME}/.bash_profile"
    cd "$PBS_O_WORKDIR"
    module load gcc/5.3.0
fi

output_dir="../analyses/ecoevolity"
if [ ! -d "$output_dir" ]
then
    mkdir -p $output_dir
fi
prefix="${output_dir}/run-${run}"

ecoevolity --seed "$seed" --prefix "$prefix" --relax-missing-sites --relax-constant-sites --relax-triallelic-sites ../configs/ecoevolity-config.yml 1>"${prefix}-ecoevolity.out" 2>&1
