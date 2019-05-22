#!/usr/bin/env python3

import argparse
from collections import Counter
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
    c = Counter()
    i = Counter()
    for g in gs:
        orc = g.original_role_counts
        if orc[':domain-of']:
            c[':domain-of'] += orc[':domain-of']
            i[':domain-of'] += 1
        if orc[':mod-of']:
            c[':mod-of'] += orc[':mod-of']
            i[':mod-of'] += 1
    print('  Normalized inversions ({} graphs : {} instances)'
          .format(sum(i.values()), sum(c.values())))
    print('    :domain-of : {} graphs : {} instances'
          .format(i[':domain-of'], c[':domain-of']))
    print('    :mod-of : {} graphs : {} instances'
          .format(i[':mod-of'], c[':mod-of']))

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
    c = Counter()
    i = Counter()
    _i = 0
    for rg in rgs:
        for r, cnt in rg.reified_counts.items():
            c[r] += cnt
            i[r] += 1
        if rg.reified_counts:
            _i += 1
    print('  Reifications ({} graphs: {} instances)'
          .format(_i, sum(c.values())))
    for _r in sorted(c, key=(lambda x: c[x]), reverse=True):
        print('    {} : {} graphs : {} instances'.format(_r, i[_r], c[_r]))

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
    c = Counter()
    i = Counter()
    _i = 0
    for cg in cgs:
        for t, cnt in cg.collapsed_counts.items():
            c[t] += cnt
            i[t] += 1
        if cg.collapsed_counts:
            _i += 1
    print('  Dereifications ({} graphs: {} instances)'
          .format(_i, sum(c.values())))
    for _t in sorted(c, key=(lambda x: c[x]), reverse=True):
        print('    {} : {} graphs : {} instances'.format(_t, i[_t], c[_t]))

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
    c = Counter()
    i = Counter()
    _i = 0
    for cr in crs:
        for t, cnt in cr.collapsed_counts.items():
            c[t] += cnt
            i[t] += 1
        if cr.collapsed_counts:
            _i += 1
    print('  Dereifications ({} graphs: {} instances)'
          .format(_i, sum(c.values())))
    for _t in sorted(c, key=(lambda x: c[x]), reverse=True):
        print('    {} : {} graphs : {} instances'.format(_t, i[_t], c[_t]))


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
