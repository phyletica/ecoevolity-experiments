#! /bin/bash
#PBS -l nodes=1:ppn=20
#PBS -l walltime=120:00:00
#PBS -l mem=120gb
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

if [ -n "$PBS_JOBNAME" ]
then
    source ${PBS_O_HOME}/.bash_profile
    cd $PBS_O_WORKDIR
fi

nprocs=8
nprior=500000
batch_size=6250
nsums=100000
sortindex=11
seed=1384268

output_dir="../prior"
if [ ! -d "$output_dir" ]
then
    mkdir -p $output_dir
fi

dmc.py --np $nprocs \
    -r 1 \
    -o ../configs/dpp-msbayes.cfg \
    -p ../configs/dpp-msbayes.cfg \
    -n $nprior \
    --num-posterior-samples $batch_size \
    --prior-batch-size $batch_size \
    --num-standardizing-samples $nsums \
    --sort-index $sortindex \
    --output-dir $output_dir \
    --seed $seed \
    --generate-samples-only \
    1>generate-prior-samples.sh.out 2>&1
