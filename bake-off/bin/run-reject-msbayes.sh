#! /bin/bash
#PBS -l nodes=1:ppn=10
#PBS -l walltime=40:00:00
#PBS -l mem=32gb
#PBS -j oe 
#PBS -l jobflags=ADVRES:jro0014_lab.56281

staging_dir=$(mktemp -d /tmp/output.XXXXXXXXX)

reps=500
nprocs=10
nprior=1000000
batch_size=10000
nsums=100000
npost=2000
nquantiles=1000
seed=37851841

output_dir="../results/msbayes"
if [ ! -d "$output_dir" ]
then
    mkdir -p $output_dir
fi

dmc.py --np $nprocs \
    -r $reps \
    -o ../configs/msbayes.cfg \
    -p ../priors/pymsbayes-results/pymsbayes-output/prior-stats-summaries \
    -n $nprior \
    --prior-batch-size $batch_size \
    --num-posterior-samples $npost \
    --num-standardizing-samples $nsums \
    -q $nquantiles \
    --sort-index 0 \
    --output-dir $output_dir \
    --temp-dir $staging_dir \
    --staging-dir $staging_dir \
    --seed $seed \
    --no-global-estimate \
    --compress

echo "Here are the contents of the local temp directory '${staging_dir}':"
ls -Fla $staging_dir
echo 'Removing the local temp directory...'
rm -r $staging_dir
echo 'Done!'

