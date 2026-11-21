import re,sys,glob
SP=re.compile(r"^([A-ZÀ-ÝČĆŠŽĐ' ]+?)((?: \([^)]*\))?):\s*(.*)$")
def stats(f):
    t=re.sub(r'<!--.*?-->','',open(f,encoding='utf-8').read(),flags=re.S)
    w=[];frag=0
    for l in t.split('\n'):
        m=SP.match(l.strip())
        if not m: continue
        txt=re.sub(r'\([^)]*\)','',m.group(3)).strip()
        n=len(re.findall(r"[\wÀ-ÿ']+",txt)); w.append(n)
        sents=[s for s in re.split(r'[.!?…]+',txt) if s.strip()]
        if n<=4: frag+=1
    short=sum(1 for x in w if x<=4)
    return len(w), sum(w)/len(w), 100*short/len(w), 100*sum(1 for x in w if x<=8)/len(w)
files=sys.argv[1:] or sorted(glob.glob('episodes/*/E*.md'))
for f in files:
    n,a,s4,s8=stats(f); print(f"{n:4d} turns  avg {a:5.1f} words  ≤4w {s4:4.1f}%  ≤8w {s8:4.1f}%  {f.split('/')[-2][:3]}{f.split('/')[-1][:3]}")
