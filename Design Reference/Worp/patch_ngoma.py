import sys,re
p=sys.argv[1];s=open(p).read()
assert 'v168' not in s.split('</style>')[0] or True
rep=[
(".wnav.live::after{content:'';width:7px;height:7px;border-radius:50%;background:#7fd2bd;box-shadow:0 0 6px #7fd2bd}",
 ".wnav.live::after{content:'';width:7px;height:7px;border-radius:50%;background:#f0e1b4;box-shadow:0 0 6px #cf8f5e}"),
('.apps2 .wp{font:400 11px "Michroma",sans-serif;letter-spacing:.14em;color:#7fd2bd;text-shadow:0 0 8px rgba(127,210,189,.55);background-image:radial-gradient(120% 160% at 25% 15%,rgba(127,210,189,.34),rgba(127,210,189,0) 60%),radial-gradient(90% 120% at 90% 100%,rgba(239,177,104,.16),rgba(239,177,104,0) 60%);background-color:#101317;animation-delay:-3.5s}',
 '.apps2 .wp{font:400 12px "Federo",serif;letter-spacing:.2em;color:#e0a072;text-shadow:0 0 8px rgba(207,143,94,.45);background-image:radial-gradient(120% 160% at 25% 15%,rgba(207,143,94,.28),rgba(207,143,94,0) 60%),radial-gradient(90% 120% at 90% 100%,rgba(240,225,180,.10),rgba(240,225,180,0) 60%);background-color:#0d0b09;animation-delay:-3.5s}   /* v168: Worp in copper and Federo, after its new look (Worp v1.26) */'),
('.apps2 .ng+.wp{border-left:1px solid #2a3139}','.apps2 .ng+.wp{border-left:1px solid #2e2620}'),
]
for a,b in rep:
  assert s.count(a)==1,a[:60]; s=s.replace(a,b)
# the portal button
i=s.index('.wportal{display:inline-flex');j=s.index('\n',i)
line=s[i:j]
line=line.replace('#2a3139','#2e2620').replace('color:#7fd2bd!important','color:#e0a072!important').replace('background-color:#101317','background-color:#0d0b09')
line=line.replace('rgba(127,210,189,.34),rgba(127,210,189,0)','rgba(207,143,94,.28),rgba(207,143,94,0)').replace('rgba(239,177,104,.16),rgba(239,177,104,0)','rgba(240,225,180,.10),rgba(240,225,180,0)').replace('rgba(127,210,189,.08)','rgba(207,143,94,.10)')
s=s[:i]+line+s[j:]
s=s.replace('.wportal .wpo{font-size:11px;color:#a9c9c0;','.wportal .wpo{font-size:11px;color:#c9b39a;')
s=s.replace('.wportal .wpw{font:400 11px "Michroma",sans-serif;letter-spacing:.14em;text-shadow:0 0 8px rgba(127,210,189,.55)}','.wportal .wpw{font:400 12px "Federo",serif;letter-spacing:.2em;text-shadow:0 0 8px rgba(207,143,94,.45)}')
s=s.replace('.wportal:hover{filter:brightness(1.15);box-shadow:0 2px 14px rgba(127,210,189,.25),inset 0 0 0 1px rgba(127,210,189,.2)}','.wportal:hover{filter:brightness(1.15);box-shadow:0 2px 14px rgba(207,143,94,.25),inset 0 0 0 1px rgba(207,143,94,.2)}')
left=[m.start() for m in re.finditer('Michroma',s)]
if s.count('Michroma')==1: s=s.replace('&family=Michroma&','&family=Federo&')
else: s=s.replace('&family=Michroma&','&family=Michroma&family=Federo&')
open(p,'w').write(s);print('ngoma ok; Michroma left:',s.count('Michroma'),'mint left:',s.count('7fd2bd'),s.count('127,210,189'))
