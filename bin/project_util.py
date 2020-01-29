#! /usr/bin/env python

import os
import sys

BIN_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(BIN_DIR)
GEKKO_SCRIPT_DIR = os.path.join(BIN_DIR, 'gekko-scripts')
GEKKO_NODATA_SCRIPT_DIR = os.path.join(BIN_DIR, 'gekko-no-data-scripts')
SIM_DIR = os.path.join(PROJECT_DIR, 'simulations')
VAL_DIR = os.path.join(SIM_DIR, 'validation')
BAKE_OFF_DIR = os.path.join(PROJECT_DIR, 'bake-off')
CONFIG_DIR = os.path.join(PROJECT_DIR, 'configs')
GEKKO_OUTPUT_DIR = os.path.join(PROJECT_DIR, 'gekko-output')
PLOT_DIR = os.path.join(VAL_DIR, "plots")

def main():
    sys.stdout.write("{0}\n".format(PROJECT_DIR))

if __name__ == '__main__':
    main()

