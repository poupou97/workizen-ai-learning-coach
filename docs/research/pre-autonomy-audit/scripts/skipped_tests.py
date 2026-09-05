"""List skipped tests from flutter test --reporter expanded log (audit evidence)."""
import re,sys
log=open(sys.argv[1],encoding='utf-8').read().splitlines()
prev=None
for i,l in enumerate(log):
    if 'chưa build' in l and prev:
        m=re.search(r'test/.*',prev)
        print(m.group(0) if m else prev.strip(), '| reason:', l.strip())
    prev=l
