#!/usr/bin/env python3

import argparse
import statistics

import norman


def main(args):
    with open(args.file) as fh:
        gs = list(norman.robust_load(fh.read()))
    re_map = norman.load_reifications(args.reify)
    co_map = norman.load_dereifications(args.collapse)

    ostats = [(len(g.variables()), len(g.triples())) for g in gs]
    print('Original:')
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))

    rgs = [norman.reify(g, re_map) for g in gs]
    assert len(rgs) == len(gs)
    diff = sum(1 if rgs[i].variables() != gs[i].variables() else 0
               for i in range(len(rgs)))
    ostats = [(len(g.variables()), len(g.triples())) for g in rgs]
    print('Reified ({} / {})'.format(diff, len(rgs)))
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))

    cgs = [norman.collapse(g, co_map) for g in gs]
    crs = [norman.collapse(g, co_map) for g in rgs]
    assert len(cgs) == len(gs)
    assert len(crs) == len(gs)
    diff = sum(1 if cgs[i].variables() != gs[i].variables() else 0
               for i in range(len(cgs)))
    ostats = [(len(g.variables()), len(g.triples())) for g in cgs]
    print('Collapsed from original ({} / {})'.format(diff, len(gs)))
    print('  Average / Total number of nodes: {:.2f} / {:d}'
          .format(statistics.mean(n for n, _ in ostats),
                  sum(n for n, _ in ostats)))
    print('  Average / Total number of edges: {:.2f} / {:d}'
          .format(statistics.mean(e for _, e in ostats),
                  sum(e for _, e in ostats)))

    diff = sum(1 if crs[i].variables() != rgs[i].variables() else 0
               for i in range(len(crs)))
    ostats = [(len(g.variables()), len(g.triples())) for g in crs]
    print('Collapsed from reified ({} / {})'.format(diff, len(gs)))
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
