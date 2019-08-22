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
    python -m smatch --pr -f "$2" "$1"
}

DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
OUT="$DIR"/out
NORM=false
EVAL=false

declare -A NORMS
NORMS[i]="--canonical-role-inversion"
NORMS[r]="--reify maps/reifications.tsv"
NORMS[a]="--reify-attributes"
NORMS[p]="--preserve-structure"
NORMS[c]="--collapse maps/dereifications.tsv"

# these are the keys of tests that are actually run
TESTS=(
    'i'
    'r'
    'a'
    'p'
    'i r'
    'i a'
    'i p'
    'r a'
    'r p'
    'a p'
    'i r a'
    'i r p'
    'r a p'
    'i r a p'
)

makeopts() { for k in $1; do printf " %s" ${NORMS[$k]}; done; }
suffix() { sed 's/ \+/./g' <<< "$1"; }

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

	# get clean file without comments
        sed '/^#/d' "$path" > "$OUT"/"$f.raw.txt"
	# sanity check that the normalizer doesn't change things
	# without requested normalizations
	python norman.py "$path" > "$OUT"/"$f.norm.txt"

	for x in "${TESTS[@]}"; do
	    suf=$( suffix "$x" )
	    python norman.py $( makeopts "$x" ) \
		   "$path" \
		   > "$OUT/$f.$suf.txt"
	done
    done
fi

if [ "$EVAL" == "true" ]; then
    g=$(basename "${1%%.txt}")
    shift  # remove gold path from "$@"

    for x in "${TESTS[@]}"; do
	suf=$( suffix "$x" )
	echo "Evaluating $g to itself ($suf)"
	evaluate "$OUT/$g.raw.txt" "$OUT/$g.$suf.txt" \
		 > "$OUT/$g.$suf.eval"
    done

    for sys in "$@"; do
        s=$(basename "${sys%%.txt}")

        echo "Evaluating $g and $s (raw)"
        evaluate "$OUT"/"$g.raw.txt" "$OUT"/"$s.raw.txt" \
		 > "$OUT"/"$s.raw.eval"

        echo "Evaluating $g and $s (norm)"
        evaluate "$OUT"/"$g.norm.txt" "$OUT"/"$s.norm.txt" \
		 > "$OUT"/"$s.norm.eval"

	for x in "${TESTS[@]}"; do
	    suf=$( suffix "$x" )
	    echo "Evaluating $g and $s ($suf)"
	    evaluate "$OUT/$g.$suf.txt" "$OUT/$s.$suf.txt" \
		     > "$OUT/$s.$suf.eval"
	done
    done
fi
