import sys
p,skin,svg,js=sys.argv[1:5]
s=open(p).read();skin=open(skin).read();svg=open(svg).read();js=open(js).read()
assert 'v1.26 skin B' not in s, 'already patched'
old='family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Michroma&'
assert old in s; s=s.replace(old,'family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Federo&')
i=s.index('</style>'); s=s[:i]+'\n'+skin+'\n'+s[i:]
old='<canvas id="ring" aria-hidden="true"></canvas>'
assert s.count(old)==1; s=s.replace(old,svg+'\n        '+old)
i=s.rindex('</script>'); s=s[:i]+js+s[i:]
open(p,'w').write(s); print('patched',len(s))
