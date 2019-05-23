#!/bin/bash

# usage: run.sh <gold-file> <sys-file> [<sys-file>...]

if [ $# -lt 2 -o ! -f "$1" -o ! -f "$2" ]; then
    echo "usage: run.sh <gold-file> <sys-file> [<sys-file>...]"
    exit 1
fi

OUT=out
EVAL=~/repos/amr-evaluation/evaluation.sh
export PYTHONPATH="$PYTHONPATH":~/repos/penman

gold="$1"; shift
mkdir -p "$OUT"

for path in "$@"; do
    [ -f "$path" ] || { echo "skipping invalid file: $path"; continue }
    f=$(basename "${path%%.txt}")
    echo "Normalizing $f" 1>&2
    sed '/^#/d' "$path" > out/"$f.raw.txt"
    python norman.py "$path" > out/"$f.norm.txt"
    python norman.py --conceptualize "$path" > out/"$f.co.txt"
    python norman.py --reify maps/reifications.tsv "$path" > out/"$f.re.txt"
    python norman.py --collapse maps/dereifications.tsv "$path" > out/"$f.de.txt"
    python norman.py --collapse maps/dereifications.tsv "out/$f.re.txt" > out/"$f.re.de.txt"
    python norman.py --reify maps/reifications.tsv --conceptualize "$path" > out/"$f.re.co.txt"
done
