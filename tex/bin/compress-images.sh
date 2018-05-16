#! /bin/bash

paths="$(ls ../../simulations/validation/plots/*nevents*.pdf)
$(ls ../../simulations/validation/plots/*scatter*pdf)
$(ls ../../bake-off/plots/*.pdf)
../images/div-cartoon/div-cartoon.pdf"

for f in $paths
do
    echo "Rasterizing and compressing $f"
    n=${f/\.pdf/-compressed\.pdf}
    convert -density 450 -compress jpeg -quality 70 $f $n
done
