#!/bin/bash

# usage: run.sh <gold-file> <sys-file> [<sys-file>...]

usage() {
cat <<EOF
Usage: run.sh [--help] [--norm|--eval] [-o DIR] GOLD SYS [SYS...]

Options:
  -h, --help            display this help message
  --norm                normalize the GOLD and SYS files
  --eval                evaluate GOLD and SYS
  -o DIR                output results to DIR/
Arguments:
  GOLD                  path to the gold AMR file
  SYS                   path to a system output
EOF
}

# redefine this as necessary
evaluate() {
    ~/repos/smatch/smatch.py --pr -f "$1" "$2"
}

DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
OUT="$DIR"/out
export PYTHONPATH="$PYTHONPATH":~/repos/penman
NORM=false
EVAL=false

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)  usage; exit 0 ;;
	--norm)     NORM=true; shift ;;
	--eval)     EVAL=true; shift ;;
        -o)         OUT=$(readlink -f "$2"); shift 2 ;;
        -*)         usage; echo "Invalid option: $1"; exit 1 ;;
        *)          break ;;
    esac
done

if [ "$NORM" != "true" -a "$EVAL" != "true" ]; then
    usage
    echo "nothing to do; use --norm or --eval"
    exit 0
fi

mkdir -p "$OUT"

if [ "$NORM" == "true" ]; then
    for path in "$@"; do
        [ -f "$path" ] || { echo "skipping invalid file: $path"; continue; }
        f=$(basename "${path%%.txt}")
        echo "Normalizing $f" 1>&2
        sed '/^#/d' "$path" > "$OUT"/"$f.raw.txt"
        python norman.py \
	       "$path" \
	       > "$OUT"/"$f.norm.txt"
        python norman.py \
	       "$path" \
	       --canonical-role-inversion \
	       > "$OUT"/"$f.cri.txt"
        python norman.py \
	       --conceptualize \
	       "$path" \
	       > "$OUT"/"$f.ca.txt"
        python norman.py \
	       --reify maps/reifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.re.txt"
        python norman.py \
	       --collapse maps/dereifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.de.txt"
        python norman.py \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.top.txt"
        python norman.py \
	       --collapse maps/dereifications.tsv \
	       "$OUT"/"$f.re.txt" \
	       > "$OUT"/"$f.re.de.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.cri.re.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       --conceptualize \
	       "$path" \
	       > "$OUT"/"$f.cri.ca.re.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.cri.re.top.txt"
    done
fi

if [ "$EVAL" == "true" ]; then
    g=$(basename "${1%%.txt}")
    shift  # remove gold path from "$@"

    echo "Evaluating $g to itself (conceptualized)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.ca.txt" \
	     > "$OUT"/"$g.ca.eval"

    echo "Evaluating $g to itself (reified)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.re.txt" \
	     > "$OUT"/"$g.re.eval"

    echo "Evaluating $g to itself (conceptualized and reified)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.cri.ca.re.txt" \
	     > "$OUT"/"$g.cri.ca.re.eval"

    for sys in "$@"; do
        s=$(basename "${sys%%.txt}")

        echo "Evaluating $g and $s (raw)"
        evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$s.raw.txt" \
		 > "$OUT"/"$s.raw.eval"

        echo "Evaluating $g and $s (norm)"
        evaluate "$OUT"/"$g.norm.txt" "$OUT"/"$s.norm.txt" \
		 > "$OUT"/"$s.norm.eval"

        echo "Evaluating $g and $s (canonicalized)"
        evaluate "$OUT"/"$g.cri.txt" "$OUT"/"$s.cri.txt" \
		 > "$OUT"/"$s.cri.eval"

        echo "Evaluating $g and $s (conceptualized)"
        evaluate "$OUT"/"$g.ca.txt" "$OUT"/"$s.ca.txt" \
		 > "$OUT"/"$s.ca.eval"

        echo "Evaluating $g and $s (reified)"
        evaluate "$OUT"/"$g.re.txt" "$OUT"/"$s.re.txt" \
		 > "$OUT"/"$s.re.eval"

        echo "Evaluating $g and $s (topped)"
        evaluate "$OUT"/"$g.top.txt" "$OUT"/"$s.top.txt" \
		 > "$OUT"/"$s.top.eval"

        echo "Evaluating $g and $s (canonicalized and reified)"
        evaluate "$OUT"/"$g.cri.re.txt" "$OUT"/"$s.cri.re.txt" \
		 > "$OUT"/"$s.cri.re.eval"

        echo "Evaluating $g and $s (canonicalized, reified, and conceptualized)"
        evaluate "$OUT"/"$g.cri.ca.re.txt" "$OUT"/"$s.cri.ca.re.txt" \
		 > "$OUT"/"$s.cri.ca.re.eval"

        echo "Evaluating $g and $s (canonicalized, reified, and topped)"
        evaluate "$OUT"/"$g.cri.re.top.txt" "$OUT"/"$s.cri.re.top.txt" \
		 > "$OUT"/"$s.cri.re.top.eval"
    done
fi
