#!/usr/bin/env python3

import sys
import re
import argparse
import csv

import penman


class RobustAMRCodec(penman.AMRCodec):
    NODE_ENTER_RE = re.compile(r'\s*(\()\s*')
    NODETYPE_RE = re.compile(r'((?:"[^"\\]*(?:\\.[^"\\]*)*")|[^\s:()\/,]*)')
    VAR_RE = re.compile('({}|{})'.format(
        penman.PENMANCodec.STRING_RE.pattern,
        penman.PENMANCodec.ATOM_RE.pattern))

    def __init__(self, *args, **kwargs):
        self._inversions['mod'] = 'domain'
        del self._deinversions['mod']
        super().__init__(*args, **kwargs)

    def encode(self, g, top=None, triples=False):
        # ensure every node has a type
        g_triples = g.triples()
        types = {t.source: t for t in g_triples if t.relation == 'instance'}
        for src in set(g.variables()).difference(types):
            g_triples.append(penman.Triple(src, 'instance', 'amr-missing'))
        g_ = penman.Graph(g_triples, g.top)
        return super().encode(g_, top=top, triples=triples)


codec = RobustAMRCodec(indent=6)


def reify(g, re_map, prefix=None):
    variables = g.variables()
    triples = []
    for triple in g.triples():
        if triple.relation in re_map:
            concept, srcrole, tgtrole = re_map[triple.relation]
            var = _unique_var(concept, variables, prefix)
            variables.add(var)
            triples.extend([
                penman.Triple(var, 'instance', concept),
                # source triple is inverse direction of original relation
                penman.Triple(var, srcrole, triple.source,
                              inverted=not triple.inverted),
                # target triple is same direction as original relation
                penman.Triple(var, tgtrole, triple.target,
                              inverted=triple.inverted)
            ])
        else:
            triples.append(triple)
    return penman.Graph(triples, top=g.top)


def _unique_var(concept, variables, prefix):
    if not prefix:
        prefix = next((c for c in concept if c.isalpha()), '_')
    var = prefix
    i = 1
    while var in variables:
        var = '{}{}'.format(prefix, i)
        i += 1
    return var


def collapse(g, co_map):
    agenda = _dereification_agenda(g, co_map)
    triples = []
    for triple in g.triples():
        if triple.source in agenda:
            incoming_triple, agendum = agenda[triple.source]
            # only replace on the relation going into the reified node
            # so the collapsed relation goes in the right spot
            if triple == incoming_triple:
                triples.extend(agendum)
        else:
            triples.append(triple)
    return penman.Graph(triples, top=g.top)


def _dereification_agenda(g, co_map):
    """
    Find eligible dereifications and return the replacements.
    """
    agenda = {}
    variables = g.variables()
    fixed = {tgt for _, _, tgt in g.edges()}.union([g.top])
    for triple in g.triples(relation='instance'):
        if triple.source not in fixed and triple.target in co_map:
            rels = {t.relation: t
                    for t in g.triples(source=triple.source)
                    if t.relation != 'instance'}
            used = set()
            agendum = []
            incoming_triple = None
            for role, src_role, tgt_role in co_map[triple.target]:
                if not (src_role in rels and tgt_role in rels):
                    continue  # source and target must exist
                src = rels[src_role]
                tgt = rels[tgt_role]
                if (src_role in used and tgt_role in used):
                    continue  # don't duplicate info
                elif src.target not in variables:
                    continue  # don't create new nodes from attributes
                agendum.append(penman.Triple(src.target, role, tgt.target,
                                             inverted=tgt.inverted))
                used.add(src_role)
                used.add(tgt_role)
                if src.inverted:
                    incoming_triple = src
                elif tgt.inverted:
                    incoming_triple = tgt
            # only include for a full mapping
            if used == set(rels):
                assert incoming_triple is not None
                agenda[triple.source] = (incoming_triple, agendum)
    return agenda


def robust_load(s):
    try:
        for g in codec.iterdecode(s):
            yield g
    except penman.DecodeError as e:
        yield from robust_load(s[e.pos+1:])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file of AMRs (or - for stdin)')
    parser.add_argument('-r', '--reify', metavar='FILE',
                        help='reify relations to nodes using mapping in FILE')
    parser.add_argument('-c', '--collapse', metavar='FILE',
                        help='collapse nodes to relations using mapping in FILE')
    parser.add_argument('--prefix', metavar='C', help='variable prefix')
    parser.add_argument('--indent', metavar='N', type=int, help='indent level')

    args = parser.parse_args()

    if args.input == '-':
        args.input = sys.stdin

    if hasattr(args.input, 'read'):
        gs = robust_load(args.input.read())
    else:
        with open(args.input) as fh:
            gs = robust_load(fh.read())

    if args.reify:
        re_map = {}
        with open(args.reify) as fh:
            reader = csv.reader(fh, delimiter='\t')
            for relation, concept, source, target in reader:
                re_map[relation] = (concept, source, target)
        gs = [reify(g, re_map, args.prefix) for g in gs]

    if args.collapse:
        co_map = {}
        with open(args.collapse) as fh:
            reader = csv.reader(fh, delimiter='\t')
            for relation, concept, source, target in reader:
                co_map.setdefault(concept, []).append(
                    (relation, source, target))
        gs = [collapse(g, co_map) for g in gs]

    if args.indent is not None:
        codec.indent = args.indent

    for g in gs:
        print(codec.encode(g))
        print()


if __name__ == '__main__':
    main()