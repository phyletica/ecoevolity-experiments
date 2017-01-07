#! /bin/bash

i=2
istart=10
istop=20
while [ "$i" -lt 101 ]
do
    subnum=$(printf "%06d" $i)
    outfile="ecoevolity-val-03pairs-dpp-batch01-sub${subnum}.sh"
    rjoutfile="ecoevolity-val-03pairs-rj-batch01-sub${subnum}.sh"
    sed -e "s/i=0/i=${istart}/g" -e "s/-lt 10/-lt ${istop}/g" \
        ecoevolity-val-03pairs-dpp-batch01-sub000001.sh \
        > "$outfile"
    sed -e "s/i=0/i=${istart}/g" -e "s/-lt 10/-lt ${istop}/g" \
        ecoevolity-val-03pairs-rj-batch01-sub000001.sh \
        > "$rjoutfile"
    chmod +x "$outfile"
    i=$(expr $i + 1)
    istart=$(expr $istart + 10)
    istop=$(expr $istop + 10)
done
