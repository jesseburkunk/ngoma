import sys
src,css,out=sys.argv[1:4]
s=open(src).read(); c=open(css).read()
i=s.rindex('</style>'); s=s[:i]+c+'\n'+s[i:]
bar='''<div class="skbar" id="skbar"><b>Skins</b>
<button data-v="">Ngoma</button><button data-v="sk-pad sk-lead-d">Lijst + donker aluminium</button><button data-v="sk-tint">Subtiel</button>
<button id="skgo">Naar Layers</button></div>
<script>(function(){let cur='sk-tint';const ap=()=>{document.body.classList.remove('sk-pad','sk-lead','sk-lead-d','sk-tint');cur.split(' ').filter(Boolean).forEach(c=>document.body.classList.add(c));
document.querySelectorAll('#skbar [data-v]').forEach(b=>b.setAttribute('aria-pressed',String(cur===b.dataset.v)))};
document.querySelectorAll('#skbar [data-v]').forEach(b=>b.onclick=()=>{cur=b.dataset.v;ap()});document.getElementById('skgo').onclick=()=>document.getElementById('padU').scrollIntoView({behavior:'smooth',block:'start'});ap();})();</script>
'''
s=s.replace('</body>',bar+'</body>',1)
open(out,'w').write(s); print('ok',len(s))
