#! /usr/bin/env python

import sys
import os
import argparse

def write_sample_table(
        npairs = 3,
        nloci = 200,
        nsites = 500,
        stream = sys.stdout):
    for pair_idx in range(npairs):
        for locus_idx in range(nloci):
            stream.write("pair{0}\tlocus{1}\t1\t1\t10\t10\t1.0\t{2}\t0.25\t0.25\t0.25\tpair{0}-locus{1}.fasta\n".format(
                    pair_idx + 1,
                    locus_idx + 1,
                    nsites))
    
def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--number-of-pairs',
            action = 'store',
            type = int,
            default = 3,
            help = 'Number of pairs.')
    parser.add_argument('-l', '--number-of-loci',
            action = 'store',
            type = int,
            default = 200,
            help = ('Number of loci.'))
    parser.add_argument('-s', '--number-of-sites',
            action = 'store',
            type = int,
            default = 500,
            help = ('Number of sites per locus.'))

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    sys.stdout.write("BEGIN SAMPLE_TBL\n")
    write_sample_table(
            npairs = args.number_of_pairs,
            nloci = args.number_of_loci,
            nsites = args.number_of_sites,
            stream = sys.stdout)
    sys.stdout.write("END SAMPLE_TBL\n")


if __name__ == "__main__":
    main_cli()
