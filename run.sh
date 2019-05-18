#!/bin/bash

DATA=data
OUT=out

mkdir -p "$OUT"

export PYTHONPATH="$PYTHONPATH":~/repos/penman

for path in "${DATA}"/*.txt; do
    f=$(basename "${path%%.txt}")
    echo "Normalizing $f" 1>&2
    python norman.py "$path" > out/"$f.norm.txt"
    python norman.py --reify maps/reifications.tsv "$path" > out/"$f.re.txt"
    python norman.py --collapse maps/dereifications.tsv "$path" > out/"$f.de.txt"
    python norman.py --collapse maps/dereifications.tsv "out/$f.re.txt" > out/"$f.rede.txt"
done
