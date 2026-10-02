# Builds public/lab-pads.html from lab_pads_template.html, the Worp engine and the Plaits wasm in public/index.html
import re,sys
root=sys.argv[1] if len(sys.argv)>1 else __import__('os').path.join(__import__('os').path.dirname(__file__),'..','..')
L=open(root+'/public/index.html').read().split('\n')
a=next(i for i,l in enumerate(L) if l.startswith('/* Worp engine for Ngoma'))
b=next(i for i in range(a,len(L)) if L[i].startswith('})();'))
eng='\n'.join(L[a:b+1])
w=next(l for l in L if l.startswith('<script id="plaits-wasm">'))
w=w[len('<script id="plaits-wasm">'):-len('</script>')]
t=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'lab_pads_template.html')).read()
t=t.replace('/*ENGINE*/',eng.replace('</script','<\\/script')).replace('/*WASM*/',w)
open(root+'/public/lab-pads.html','w').write(t); print(len(t))
