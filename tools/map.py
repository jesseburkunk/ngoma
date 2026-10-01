"""Regenerates the index part of tools/MAP.md (everything under the AUTO marker). Run: python3 tools/map.py
The handwritten part above the marker stays as it is."""
import os,re
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,'..')
FILES=[('public/index.html','Ngoma'),('public/worp/index.html','Worp')]
MARK='<!-- AUTO: below this line tools/map.py writes; do not edit by hand -->'
sec_re=re.compile(r'^\s*(?:/\*\s*(?:=+|-{5,})\s*(.*?)\s*(?:-{3,}.*)?$|([A-Z][A-Z ,:+()/&-]{3,})\s*(?:\(.*)?$)')
fn_re=re.compile(r'^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)|^(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:\(|[A-Za-z_$][\w$]*\s*=>|async|function)|^class\s+([A-Za-z_$][\w$]*)')
def index(path,title):
    L=open(os.path.join(ROOT,path),encoding='utf-8').read().split('\n')
    out=[f'## {title}: {path} ({len(L)} lines)','']
    cur=None; items=[]
    def flush():
        if cur is None and not items: return
        name,ln=cur if cur else ('(start)',1)
        out.append(f'- **{name}** (line {ln}): '+(', '.join(f'{n} {l}' for n,l in items) if items else '(no functions)'))
    prev_eq=False
    for i,raw in enumerate(L,1):
        s=raw.strip()
        head=None
        m=re.match(r'^/\*\s*-{5,}\s*(.+?)(?:\s*-{3,}.*)?$',s)
        if m: head=m.group(1)
        if prev_eq and re.match(r'^[A-Z][A-Z ,:+()/&.-]{3,}',s): head=s.split('(')[0].strip()
        prev_eq=bool(re.match(r'^/\*\s*={5,}\s*$',s))
        if head:
            head=re.sub(r'\s*\*/\s*$','',head); head=head[:90]
            flush(); cur=(head,i); items=[]; continue
        if s.startswith('<script'): flush(); cur=('script starts',i); items=[]; continue
        if raw[:1] in (' ','\t'): continue
        f=fn_re.match(raw)
        if f: items.append((next(g for g in f.groups() if g),i))
    flush(); out.append(''); return '\n'.join(out)
mp=os.path.join(HERE,'MAP.md'); txt=open(mp,encoding='utf-8').read() if os.path.exists(mp) else MARK
top=txt.split(MARK)[0].rstrip()+'\n\n'+MARK+'\n\n'
open(mp,'w',encoding='utf-8').write(top+'\n'.join(index(p,t) for p,t in FILES))
print('MAP.md index rewritten')
