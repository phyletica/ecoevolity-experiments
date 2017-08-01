#!/bin/sh

NSPECIES=2
NGENOMES=10
NCHARS=500000

i=1
while [ "$i" -lt 9 ]
do
    prefix="c${i}sp"
    outfile="../alignments/comp0${i}-${NSPECIES}species-${NGENOMES}genomes-${NCHARS}chars.nex"
    ./generate-dummy-biallelic-alignment.py \
        --nspecies "$NSPECIES" \
        --ngenomes "$NGENOMES" \
        --ncharacters "$NCHARS" \
        --prefix "$prefix" \
        > "$outfile"
    i=`expr $i + 1`
done

# Generate 100k dummy alignements
NCHARS=100000

i=1
while [ "$i" -lt 9 ]
do
    prefix="c${i}sp"
    outfile="../alignments/comp0${i}-${NSPECIES}species-${NGENOMES}genomes-${NCHARS}chars.nex"
    ./generate-dummy-biallelic-alignment.py \
        --nspecies "$NSPECIES" \
        --ngenomes "$NGENOMES" \
        --ncharacters "$NCHARS" \
        --prefix "$prefix" \
        > "$outfile"
    i=`expr $i + 1`
done

# Generate 40k dummy alignements
NCHARS=40000

i=1
while [ "$i" -lt 4 ]
do
    prefix="c${i}sp"
    outfile="../alignments/comp0${i}-${NSPECIES}species-${NGENOMES}genomes-0${NCHARS}chars.nex"
    ./generate-dummy-biallelic-alignment.py \
        --nspecies "$NSPECIES" \
        --ngenomes "$NGENOMES" \
        --ncharacters "$NCHARS" \
        --prefix "$prefix" \
        > "$outfile"
    i=`expr $i + 1`
done

