#!/usr/bin/python3

import sys
import re

import norman


if not len(sys.argv) == 5:
    sys.exit('usage: id-align.py <lhs-in> <rhs-in> <lhs-out> <rhs-out>')

codec = norman.RobustAMRCodec(indent=6)


def accumulate(f, d):
    curid = None
    lines = []
    for line in open(f):
        if line.startswith('#') and '::id' in line:
            if curid:
                g = next(codec.iterdecode('\n'.join(lines)), None)
                if g:
                    d[curid] = g
            curid = re.search(r'::id ([^ $]+)(?: |$)', line).group(1)
            lines = []
        elif curid and not line.startswith('#'):
            lines.append(line)
    return d


lhs = accumulate(sys.argv[1], {})
rhs = accumulate(sys.argv[2], {})

shared = set(lhs).intersection(rhs)

if len(shared) < len(lhs):
    print('{} unaligned on lhs: {}'
          .format(len(lhs) - len(shared),
                  ', '.join(sorted(set(lhs) - shared))),
          file=sys.stderr)
if len(shared) < len(rhs):
    print('{} unaligned on rhs: {}'
          .format(len(rhs) - len(shared),
                  ', '.join(sorted(set(rhs) - shared))),
          file=sys.stderr)

with open(sys.argv[3], 'w') as lfh, open(sys.argv[4], 'w') as rfh:
    for id in sorted(shared):
        print('# ::id {}'.format(id), file=lfh)
        print(codec.encode(lhs[id]), file=lfh)
        print(file=lfh)

        print('# ::id {}'.format(id), file=rfh)
        print(codec.encode(rhs[id]), file=rfh)
        print(file=rfh)
