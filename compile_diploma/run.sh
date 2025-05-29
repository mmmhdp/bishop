#!/usr/bin/env bash

#set -e 
#
#mkdir -p ./test
#rm -rf ./test/*
#
#cp ~/Downloads/thesis_bishop.zip ./test
#unzip -o ./test/thesis_bishop.zip -d ./test

cd ./test

latexmk -C
latexmk -pdf -interaction=nonstopmode -r ../LatexMk mthesis.tex -f
biber mthesis
latexmk -pdf -interaction=nonstopmode -r ../LatexMk mthesis.tex -f

