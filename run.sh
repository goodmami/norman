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
    ~/repos/smatch/smatch.py --pr -f "$2" "$1"
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
	       > "$OUT"/"$f.i.txt"
        python norman.py \
	       --conceptualize \
	       "$path" \
	       > "$OUT"/"$f.a.txt"
        python norman.py \
	       --reify maps/reifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.r.txt"
        python norman.py \
	       --collapse maps/dereifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.d.txt"
        python norman.py \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.t.txt"
        python norman.py \
	       --collapse maps/dereifications.tsv \
	       "$OUT"/"$f.r.txt" \
	       > "$OUT"/"$f.r.d.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --conceptualize \
	       "$path" \
	       > "$OUT"/"$f.i.a.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.i.r.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.i.t.txt"
        python norman.py \
	       --conceptualize \
	       --reify maps/reifications.tsv \
	       "$path" \
	       > "$OUT"/"$f.a.r.txt"
        python norman.py \
	       --conceptualize \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.a.t.txt"
        python norman.py \
	       --reify maps/reifications.tsv \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.r.t.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       --conceptualize \
	       "$path" \
	       > "$OUT"/"$f.i.a.r.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --conceptualize \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.i.a.t.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --reify maps/reifications.tsv \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.i.r.t.txt"
        python norman.py \
	       --conceptualize \
	       --reify maps/reifications.tsv \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.a.r.t.txt"
        python norman.py \
	       --canonical-role-inversion \
	       --conceptualize \
	       --reify maps/reifications.tsv \
	       --node-tops \
	       "$path" \
	       > "$OUT"/"$f.i.a.r.t.txt"
    done
fi

if [ "$EVAL" == "true" ]; then
    g=$(basename "${1%%.txt}")
    shift  # remove gold path from "$@"

    echo "Evaluating $g to itself (attr-re)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.a.txt" \
	     > "$OUT"/"$g.a.eval"

    echo "Evaluating $g to itself (relation-re)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.r.txt" \
	     > "$OUT"/"$g.r.eval"

    echo "Evaluating $g to itself (attr-re and relation-re)"
    evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$g.a.r.txt" \
	     > "$OUT"/"$g.a.r.eval"

    for sys in "$@"; do
        s=$(basename "${sys%%.txt}")

        echo "Evaluating $g and $s (raw)"
        evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$s.raw.txt" \
		 > "$OUT"/"$s.raw.eval"

        echo "Evaluating $g and $s (norm)"
        evaluate "$OUT"/"$g.norm.txt" "$OUT"/"$s.norm.txt" \
		 > "$OUT"/"$s.norm.eval"

        echo "Evaluating $g and $s (inv)"
        evaluate "$OUT"/"$g.i.txt" "$OUT"/"$s.i.txt" \
		 > "$OUT"/"$s.i.eval"

        echo "Evaluating $g and $s (attr-re)"
        evaluate "$OUT"/"$g.a.txt" "$OUT"/"$s.a.txt" \
		 > "$OUT"/"$s.a.eval"

        echo "Evaluating $g and $s (relation-re)"
        evaluate "$OUT"/"$g.r.txt" "$OUT"/"$s.r.txt" \
		 > "$OUT"/"$s.r.eval"

        echo "Evaluating $g and $s (topped)"
        evaluate "$OUT"/"$g.t.txt" "$OUT"/"$s.t.txt" \
		 > "$OUT"/"$s.t.eval"

        echo "Evaluating $g and $s (inv and attr-re)"
        evaluate "$OUT"/"$g.i.a.txt" "$OUT"/"$s.i.a.txt" \
		 > "$OUT"/"$s.i.a.eval"

        echo "Evaluating $g and $s (inv and relation-re)"
        evaluate "$OUT"/"$g.i.r.txt" "$OUT"/"$s.i.r.txt" \
		 > "$OUT"/"$s.i.r.eval"

        echo "Evaluating $g and $s (inv and topped)"
        evaluate "$OUT"/"$g.i.t.txt" "$OUT"/"$s.i.t.txt" \
		 > "$OUT"/"$s.i.t.eval"

        echo "Evaluating $g and $s (attr-re and relation-re)"
        evaluate "$OUT"/"$g.a.r.txt" "$OUT"/"$s.a.r.txt" \
		 > "$OUT"/"$s.a.r.eval"

        echo "Evaluating $g and $s (inv, attr-re, and relation-re)"
        evaluate "$OUT"/"$g.i.a.r.txt" "$OUT"/"$s.i.a.r.txt" \
		 > "$OUT"/"$s.i.a.r.eval"

        echo "Evaluating $g and $s (inv, attr-re, and topped)"
        evaluate "$OUT"/"$g.i.a.t.txt" "$OUT"/"$s.i.a.t.txt" \
		 > "$OUT"/"$s.i.a.t.eval"

        echo "Evaluating $g and $s (inv, relation-re, and topped)"
        evaluate "$OUT"/"$g.i.r.t.txt" "$OUT"/"$s.i.r.t.txt" \
		 > "$OUT"/"$s.i.r.t.eval"

        echo "Evaluating $g and $s (attr-re, relation-re, and topped)"
        evaluate "$OUT"/"$g.a.r.t.txt" "$OUT"/"$s.a.r.t.txt" \
		 > "$OUT"/"$s.a.r.t.eval"

        echo "Evaluating $g and $s (inv, attr-re, relation-re, and topped)"
        evaluate "$OUT"/"$g.i.a.r.t.txt" "$OUT"/"$s.i.a.r.t.txt" \
		 > "$OUT"/"$s.i.a.r.t.eval"
    done
fi
