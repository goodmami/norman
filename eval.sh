#!/bin/bash

DATA=data
OUT=out
EVAL=~/repos/amr-evaluation/evaluation.sh

export PYTHONPATH="$PYTHONPATH":~/repos/penman

for path in "${DATA}"/*.txt; do
    f=$(basename "${path%%.txt}")
    echo "Comparing $path to $f.norm" 1>&2
    "${SMATCH}"/smatch.py --pr -f "$path" out/"$f.norm.txt"
    echo "Comparing $f.norm to $f.re" 1>&2
    "${SMATCH}"/smatch.py --pr -f out/"$f.norm.txt" out/"$f.re.txt"
    echo "Comparing $f.norm to $f.de" 1>&2
    "${SMATCH}"/smatch.py --pr -f out/"$f.norm.txt" out/"$f.de.txt"
    echo "Comparing $f.re to $f.de" 1>&2
    "${SMATCH}"/smatch.py --pr -f out/"$f.re.txt" out/"$f.de.txt"
done
