#!/usr/bin/env python3
"""Usage: python3 check_analysis.py EP_NUMBER [EP_NUMBER ...]
Checks denmark/analysis_md/partN/epXX.md against denmark/episodes/partN/epXX.md."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def part(n): return 1 + (n - 1) // 15
SECTIONS = ['■ 주요 단어', '■ 문법', '■ 표현', '■ 시제·어순']
ok_all = True
for a in sys.argv[1:]:
    n = int(a); p = part(n)
    src = open(f'{ROOT}/episodes/part{p}/ep{n:02d}.md', encoding='utf-8').read().split('\n## 학습 노트')[0]
    turns = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r'^(\d+)\. (.*)$', src, re.M)}
    path = f'{ROOT}/analysis_md/part{p}/ep{n:02d}.md'
    if not os.path.exists(path): print(f'ep{n:02d}: MISSING'); ok_all = False; continue
    txt = open(path, encoding='utf-8').read()
    blocks = re.split(r'^### ', txt, flags=re.M)[1:]
    errs = []
    seen = []
    for b in blocks:
        head, _, body = b.partition('\n')
        m = re.match(r'(\d+)\. (.*)$', head.strip())
        if not m: errs.append(f'bad heading: {head[:50]}'); continue
        k = int(m.group(1)); seen.append(k)
        if turns.get(k) != m.group(2).strip(): errs.append(f'turn {k}: heading text differs from source')
        if not re.search(r'^번역: \S', body, re.M): errs.append(f'turn {k}: no 번역')
        for s in SECTIONS:
            if s not in body: errs.append(f'turn {k}: missing {s}')
        if not re.search(r'^\| .+ \| .+ \| .+ \|$', body, re.M): errs.append(f'turn {k}: no word-table row')
    if seen != list(range(1, 121)): errs.append(f'turn numbers not 1..120 (got {len(seen)})')
    print(f'ep{n:02d}: ' + ('OK' if not errs else f'{len(errs)} problems: ' + '; '.join(errs[:8])))
    ok_all &= not errs
sys.exit(0 if ok_all else 1)
