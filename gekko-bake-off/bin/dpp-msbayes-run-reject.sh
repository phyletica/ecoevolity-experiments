#! /bin/sh

nprocs=8
nprior=500000
batch_size=6250
nsums=100000
npost=5000
nquantiles=5000
sort_index=11
seed=9846243512

output_dir="../analyses/pymsbayes/posterior"
if [ ! -d "$output_dir" ]
then
    mkdir -p $output_dir
fi

dmc.py --np $nprocs \
    -o ../configs/dpp-msbayes-300-424654214.cfg \
    -p ../analyses/pymsbayes/prior/pymsbayes-results/pymsbayes-output/prior-stats-summaries \
    -n $nprior \
    --prior-batch-size $batch_size \
    --num-posterior-samples $npost \
    --num-standardizing-samples $nsums \
    -q $nquantiles \
    --sort-index $sort_index \
    --output-dir $output_dir \
    --stat-prefixes pi pi.b \
    --seed $seed \
    --compress \
    1>dpp-msbayes-run-reject.sh.out 2>&1
