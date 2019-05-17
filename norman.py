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


def reify(g, reifications, prefix=None):
    variables = g.variables()
    triples = []
    for triple in g.triples():
        if triple.relation in reifications:
            concept, srcrole, tgtrole = reifications[triple.relation]
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


def dereify(g, dereifications):
    eligible = _eligible_dereifications(g, dereifications)
    triples = []
    for triple in g.triples():
        if triple.source in candidates:
            
    agenda = _dereification_agenda(g, dereifications)
    triples = []
    for triple in g.triples():
        if triple.source in agenda:
            triples.extend(agenda[triple.source])
            # clear agenda but don't remove key so we can still remove
            # the remaining dereified relations
            agenda[triple.source] = []
        else:
            triples.append(triple)
    return penman.Graph(triples, top=g.top)


def _eligible_dereifications(g, dereifications):
    # initially consider all with matching concepts
    candidates = {src for src, role, tgt in g.triples()
                  if (role == 'instance'
                      and tgt in dereifications)}
    # filter "fixed" nodes: those that are the target in a relation
    candidates -= {tgt for _, _, tgt in g.edges()}.union([g.top])
    # filter those without the necessary relations
    relmap = {}
    for src, rel, tgt in g.triples():
        relmap.setdefault(src, {}).setdefault(rel, []).append(tgt)
    candidates -= {}


def _dereification_agenda(g, dereifications):
    """
    Find eligible dereifications and return the replacements.
    """
    agenda = {}
    fixed = {tgt for _, _, tgt in g.edges()}.union([g.top])
    for triple in g.triples(relation='instance'):
        if triple.source not in fixed and triple.target in dereifications:
            rels = {t.relation: t
                    for t in g.triples(source=triple.source)
                    if t.relation != 'instance'}
            used = set()
            agendum = []
            for role, src_role, tgt_role in dereifications[triple.target]:
                if src_role in rels and tgt_role in rels:
                    _src = rels[src_role].target
                    _tgt = rels[tgt_role].target
                    inverted = rels[tgt_role].inverted
                    agendum.append(penman.Triple(_src, role, _tgt,
                                                 inverted=inverted))
                    used.add(src_role)
                    used.add(tgt_role)
            # only include for a full mapping
            if used == set(rels):
                agenda[triple] = agendum
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
                        help='reify relations using reifications in FILE')
    parser.add_argument('-d', '--dereify', metavar='FILE',
                        help='dereify relations using reifications in FILE')
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
        reifications = {}
        with open(args.reify) as fh:
            reader = csv.reader(fh, delimiter='\t')
            for relation, concept, source, target in reader:
                reifications[relation] = (concept, source, target)
        gs = [reify(g, reifications, args.prefix) for g in gs]

    if args.dereify:
        dereifications = {}
        with open(args.dereify) as fh:
            reader = csv.reader(fh, delimiter='\t')
            for relation, concept, source, target in reader:
                dereifications.setdefault(concept, []).append(
                    (relation, source, target))
        gs = [dereify(g, dereifications) for g in gs]

    if args.indent is not None:
        codec.indent = args.indent

    for g in gs:
        print(codec.encode(g))
        print()


if __name__ == '__main__':
    main()
