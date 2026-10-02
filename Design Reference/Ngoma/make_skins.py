import sys
src,css,out=sys.argv[1:4]
s=open(src).read(); c=open(css).read()
i=s.rindex('</style>'); s=s[:i]+c+'\n'+s[i:]
bar='''<div class="skbar" id="skbar"><b>Skins</b>
<span>Pad:</span><button data-g="pad" data-v="">Ngoma</button><button data-g="pad" data-v="sk-pad">Lijst</button>
<span>Lead:</span><button data-g="lead" data-v="">Ngoma</button><button data-g="lead" data-v="sk-lead">Aluminium licht</button><button data-g="lead" data-v="sk-lead-d">Aluminium donker</button>
<button id="skgo">Naar Layers</button></div>
<script>(function(){const st={pad:'sk-pad',lead:'sk-lead'};const ap=()=>{document.body.classList.remove('sk-pad','sk-lead','sk-lead-d');if(st.pad)document.body.classList.add(st.pad);if(st.lead)document.body.classList.add(st.lead);
document.querySelectorAll('#skbar [data-g]').forEach(b=>b.setAttribute('aria-pressed',String(st[b.dataset.g]===b.dataset.v)))};
document.querySelectorAll('#skbar [data-g]').forEach(b=>b.onclick=()=>{st[b.dataset.g]=b.dataset.v;ap()});document.getElementById('skgo').onclick=()=>document.getElementById('padU').scrollIntoView({behavior:'smooth',block:'start'});ap();})();</script>
'''
s=s.replace('</body>',bar+'</body>',1)
open(out,'w').write(s); print('ok',len(s))
