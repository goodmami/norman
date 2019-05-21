#!/usr/bin/env python3

import argparse
import statistics

import norman


def main(args):
    with open(args.file) as fh:
        gs = list(norman.robust_load(fh.read()))
    ostats = [(len(g.variables()), len(g.triples())) for g in gs]
    print('Original:')
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))

    re_map = norman.load_reifications(args.reify)
    co_map = norman.load_dereifications(args.collapse)

    gs_ = [norman.reify(g, re_map) for g in gs]
    assert len(gs_) == len(gs)
    diff = sum(1 if gs_[i].variables() != gs[i].variables() else 0
               for i in range(len(gs_)))
    gs = gs_
    ostats = [(len(g.variables()), len(g.triples())) for g in gs]
    print('Reified ({} / {})'.format(diff, len(gs)))
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))

    gs_ = [norman.collapse(g, co_map) for g in gs]
    assert len(gs_) == len(gs)
    diff = sum(1 if gs_[i].variables() != gs[i].variables() else 0
               for i in range(len(gs_)))
    gs = gs_
    ostats = [(len(g.variables()), len(g.triples())) for g in gs]
    print('Collapsed ({} / {})'.format(diff, len(gs)))
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='a file containing AMRs')
    parser.add_argument('-r', '--reify', metavar='FILE',
                        required=True,
                        help='reification mapping')
    parser.add_argument('-c', '--collapse', metavar='FILE',
                        required=True,
                        help='dereification mapping')

    args = parser.parse_args()
    main(args)
