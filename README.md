
# Norman: Normalized PENMAN (AMR)

This is the code associated with the paper [*AMR Normalization for
Fairer Evaluation*](https://arxiv.org/abs/1909.01568).

If you are interested in using the normalization procedures with AMR,
the next version of the [Penman][] project will incorporate the
methods described by the paper. This repository is for reproducing the
experiments of the paper.

[Penman]: https://github.com/goodmami/penman

## Citation

``` bibtex
@inproceedings{Goodman:2019,
  title     = "{AMR} Normalization for Fairer Evaluation",
  author    = "Goodman, Michael Wayne",
  booktitle = "Proceedings of the 33rd Pacific Asia Conference on Language, Information, and Computation",
  year      = "2019",
  address   = "Hakodate"
}
```

## Running the Experiment

### Setup

Python 3.5+ is required to run the experiment. First clone the
repository and create a virtual environment, then install `norman` and
its dependencies:

``` console
[~]$ git clone https://github.com/goodmami/norman.git
[...]
[~]$ cd norman/
[~/norman]$ python3 -m venv env
[~/norman]$ source env/bin/activate
(env) [~/norman]$ pip install .
[...]
```

Download the Little Prince corpus v1.6 training data if you don't have
it already:

``` console
(env) [~/norman]$ mkdir data/
(env) [~/norman]$ wget -P data/ https://amr.isi.edu/download/amr-bank-struct-v1.6-training.txt
```

For reproducibility, the outputs of [JAMR][], [CAMR][], and
[AMREager][] used in the paper are included in the `sys/`
subdirectory, but at this point you may wish to parse with other
parsers for additional comparisons.

[JAMR]: https://github.com/jflanigan/jamr
[CAMR]: https://github.com/c-amr/camr
[AMREager]: http://cohort.inf.ed.ac.uk/amreager.html

### Normalizing

Call `run.sh` with `--norm`, a path to a gold AMR file, and paths to
any system outputs.

``` console
(env) [~/norman]$ ./run.sh --norm \
> data/amr-bank-struct-v1.6-training.txt \
> sys/amr-bank-struct-v1.6-training.jamr.txt \
> sys/amr-bank-struct-v1.6-training.camr.txt \
> sys/amr-bank-struct-v1.6-training.amr-eager.txt
```

If you want to modify which tests are performed, inspect `run.sh` and
edit the `TESTS` variable accordingly. Note that the tests are
referenced by keys:

* `i` -- canonical role inversion
* `r` -- relation reification
* `a` -- attribute reification
* `p` -- structure preservation

### Evaluating

Call `run.sh` with `--eval`, a path to a gold AMR file, and paths to
any system outputs. Note that these are the paths to the original
files, not the normalized ones.

``` console
(env) [~/norman]$ ./run.sh --eval \
> data/amr-bank-struct-v1.6-training.txt \
> sys/amr-bank-struct-v1.6-training.jamr.txt \
> sys/amr-bank-struct-v1.6-training.camr.txt \
> sys/amr-bank-struct-v1.6-training.amr-eager.txt
```

### Corpus Statistics

Some of the statistics in the paper regarding the normalizability of
the gold and system AMR files were produced using
`util/corpus-stats.py`. Run it (e.g., for the gold file) as follows:

``` console
(env) [~/norman]$ python util/corpus-stats.py \
> -r maps/reifications.tsv \
> -c maps/dereifications.tsv \
> data/amr-bank-struct-v1.6-training.txt
```
