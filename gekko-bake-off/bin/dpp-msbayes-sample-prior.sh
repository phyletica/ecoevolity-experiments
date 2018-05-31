#! /bin/sh

nprocs=8
nprior=500000
batch_size=6250
nsums=100000
sort_index=11
seed=845225390

output_dir="../analyses/pymsbayes/prior"
if [ ! -d "$output_dir" ]
then
    mkdir -p $output_dir
fi

dmc.py --np $nprocs \
    -o ../configs/dpp-msbayes-300-424654214.cfg \
    -p ../configs/dpp-msbayes-300-424654214.cfg \
    -n $nprior \
    --prior-batch-size $batch_size \
    --num-posterior-samples $batch_size \
    --num-standardizing-samples $nsums \
    --sort-index $sort_index \
    --output-dir $output_dir \
    --stat-prefixes pi pi.b \
    --seed $seed \
    --generate-samples-only \
    1>dpp-msbayes-sample-prior.sh.out 2>&1
