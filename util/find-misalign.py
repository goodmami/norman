
import sys

import norman

codec = norman.RobustAMRCodec(indent=2)

g1s = list(codec.iterdecode(open(sys.argv[1]).read()))
g2s = list(codec.iterdecode(open(sys.argv[2]).read()))

print(len(g1s), len(g2s))

for i in range(max(len(g1s), len(g2s))):
    g1 = g1s[i]
    g2 = g2s[i]
    if g1.top != g2.top:
        print(i)
        print(codec.encode(g1))
        print(codec.encode(g2))
