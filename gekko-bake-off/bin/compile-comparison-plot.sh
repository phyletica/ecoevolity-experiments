#! /bin/bash

cd ../results
latexmk -pdf comparison.tex && pdfcrop comparison.pdf comparison.pdf
