#! /usr/bin/env bash

for j in pairs-1-lines-crop pairs-1-labels-crop pairs-2-1-lines-crop pairs-2-1-labels-crop pairs-2-2-lines-crop pairs-2-2-labels-crop pairs-2-3-lines-crop pairs-2-3-labels-crop pairs-3-lines-crop pairs-3-labels-crop
do
    pdflatex "--jobname=$j" div-models-master.tex
done

for i in pairs*crop.pdf
do
    pdfcrop "$i" "$i"
done

pdflatex "--jobname=div-cartoon" div-cartoon-master.tex

pdfcrop "div-cartoon.pdf" "div-cartoon.pdf"
