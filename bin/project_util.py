#! /usr/bin/env python

import os
import sys

BIN_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(BIN_DIR)

def main():
    sys.stdout.write("{0}\n".format(PROJECT_DIR))

if __name__ == '__main__':
    main()

