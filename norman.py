#!/usr/bin/env python3

import sys
import re
import argparse
import csv
from collections import defaultdict

import penman


class RobustAMRCodec(penman.PENMANCodec):
    NODE_ENTER_RE = re.compile(r'\s*(\()\s*')
    NODETYPE_RE = re.compile(r'((?:"[^"\\]*(?:\\.[^"\\]*)*")|[^\s:()\/]*)')
    VAR_RE = re.compile('({}|{})'.format(
        penman.PENMANCodec.STRING_RE.pattern,
        penman.PENMANCodec.ATOM_RE.pattern))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canonical_role_inversion = False

    def handle_triple(self, lhs, relation, rhs):
        if self.canonical_role_inversion:
            if relation == ':mod-of':
                relation = ':domain'
            elif relation == ':domain-of':
                relation = ':mod'
            elif relation == ':consist':
                relation = ':consist-of-of'
            elif relation == ':prep-on-behalf':
                relation = ':prep-on-behalf-of-of'
            elif relation == ':prep-out':
                relation = ':prep-out-of-of'
        return super().handle_triple(lhs, relation, rhs)

    def is_relation_inverted(self, relation):
        if self.canonical_role_inversion:
            if relation in ('consist-of', 'prep-on-behalf-of', 'prep-out-of'):
                return False
        return super().is_relation_inverted(relation)

    def invert_relation(self, relation):
        if self.canonical_role_inversion:
            if relation in ('consist-of', 'prep-on-behalf-of', 'prep-out-of'):
                return relation + '-of'
            elif relation == 'mod':
                return 'domain'
            elif relation == 'domain':
                return 'mod'
        return super().invert_relation(relation)

    def triples_to_graph(self, triples, top=None):
        counts = defaultdict(int)
        for triple in triples:
            rel = triple[1]
            counts[rel] += 1
        g = super().triples_to_graph(triples, top=top)
        g.original_role_counts = counts
        return g


codec = RobustAMRCodec(indent=6)


def reify(g, re_map, prefix=None):
    variables = g.variables()
    counts = defaultdict(int)
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
            counts[triple.relation] += 1
        else:
            triples.append(triple)
    g = penman.Graph(triples, top=g.top)
    g.reified_counts = counts
    return g


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
    counts = defaultdict(int)
    types = {t.source: t.target for t in g.triples()
             if t.relation == 'instance'}
    triples = []
    for triple in g.triples():
        if triple.source in agenda:
            incoming_triple, agendum = agenda[triple.source]
            # only replace on the relation going into the reified node
            # so the collapsed relation goes in the right spot
            if triple == incoming_triple:
                triples.extend(agendum)
                counts[types.get(triple.source, '?')] += 1
        else:
            triples.append(triple)
    g = penman.Graph(triples, top=g.top)
    g.collapsed_counts = counts
    return g


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


def conceptualize(g):
    variables = g.variables()
    # filter out triples with empty instances
    triples = [t for t in g.triples()
               if t.relation != 'instance' or t.target]
    # ensure every node has a type
    # types = {t.source: t for t in triples if t.relation == 'instance'}
    # for src in variables.difference(types):
    #     triples.append(penman.Triple(src, 'instance', 'amr-missing'))
    # ensure constants are nodes
    new_triples = []
    for triple in triples:
        if triple.relation != 'instance' and triple.target not in variables:
            var = _unique_var('', variables, '_')
            new_triples.extend([
                penman.Triple(var, 'instance', triple.target),
                penman.Triple(triple.source, triple.relation, var)
            ])
            variables.add(var)
        else:
            new_triples.append(triple)

    return penman.Graph(new_triples, g.top)


def robust_load(s, node_tops=False):
    if node_tops:
        lines = []
        for line in s.splitlines():
            if line.startswith('#'):
                continue
            else:
                lines.append(
                    re.sub(r'(:[^ ]*)\s+\(([^ /]+)\s*\/',
                           r':TOP \2 \1 (\2 /',
                           line))
        s = '\n'.join(lines)

    try:
        for g in codec.iterdecode(s):
            yield g
    except penman.DecodeError as e:
        yield from robust_load(s[e.pos+1:], node_tops)


def load_reifications(f):
    re_map = {}
    with open(f) as fh:
        reader = csv.reader(fh, delimiter='\t')
        for relation, concept, source, target in reader:
            re_map[relation] = (concept, source, target)
    return re_map


def load_dereifications(f):
    co_map = {}
    with open(f) as fh:
        reader = csv.reader(fh, delimiter='\t')
        for relation, concept, source, target in reader:
            co_map.setdefault(concept, []).append(
                (relation, source, target))
    return co_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file of AMRs (or - for stdin)')
    parser.add_argument(
        '-i', '--canonical-role-inversion',
        action='store_true',
        help='canonicalize role inversions')
    parser.add_argument('-r', '--reify', metavar='FILE',
                        help='reify relations to nodes using mapping in FILE')
    parser.add_argument(
        '-c', '--collapse', metavar='FILE',
        help='collapse nodes to relations using mapping in FILE')
    parser.add_argument('--conceptualize', action='store_true',
                        help='ensure every node has a concept')
    parser.add_argument('--node-tops', action='store_true',
                        help='add relations to mark non-reentrant relations')
    parser.add_argument('--prefix', metavar='C', help='variable prefix')
    parser.add_argument('--indent', metavar='N', type=int, help='indent level')
    parser.add_argument('--triples', action='store_true',
                        help='output triples')

    args = parser.parse_args()

    if args.input == '-':
        args.input = sys.stdin
    if args.indent:
        codec.indent = args.indent
    if args.canonical_role_inversion:
        codec.canonical_role_inversion = True

    if hasattr(args.input, 'read'):
        gs = robust_load(args.input.read(), args.node_tops)
    else:
        with open(args.input) as fh:
            gs = robust_load(fh.read(), args.node_tops)

    if args.reify:
        re_map = load_reifications(args.reify)
        gs = [reify(g, re_map, args.prefix) for g in gs]

    if args.collapse:
        co_map = load_dereifications(args.collapse)
        gs = [collapse(g, co_map) for g in gs]

    if args.conceptualize:
        gs = [conceptualize(g) for g in gs]

    for g in gs:
        print(codec.encode(g, triples=args.triples))
        print()


if __name__ == '__main__':
    main()
