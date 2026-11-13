#!/usr/bin/env python3
"""apply_fix.py EP TURN OLD NEW — fix a turn in source episode + matching analysis heading/block."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ep, turn, old, new = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
p = (ep - 1) // 15 + 1
src = f'{ROOT}/episodes/part{p}/ep{ep:02d}.md'
s = open(src, encoding='utf-8').read()
pat = re.compile(rf'^({turn}\. .*)$', re.M); m = pat.search(s)
assert m and old in m.group(1), f'source ep{ep} t{turn}: "{old}" not found'
s = s[:m.start()] + m.group(1).replace(old, new) + s[m.end():]
open(src, 'w', encoding='utf-8').write(s)
ana = f'{ROOT}/analysis_md/part{p}/ep{ep:02d}.md'
if os.path.exists(ana):
    a = open(ana, encoding='utf-8').read()
    m = re.search(rf'^### {turn}\. .*?(?=^### |\Z)', a, re.M | re.S)
    if m:
        blk = m.group(0)
        a = a[:m.start()] + blk.replace(old, new) + a[m.end():]
        open(ana, 'w', encoding='utf-8').write(a)
        print(f'ep{ep} t{turn}: fixed source + analysis ({blk.count(old)} occurrences in block)')
        print(re.search(rf'^### {turn}\. .*?(?=^### |\Z)', a, re.M | re.S).group(0))
        sys.exit()
print(f'ep{ep} t{turn}: fixed source only')
