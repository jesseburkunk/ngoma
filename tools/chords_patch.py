#!/usr/bin/env python3
"""v156 Chords: one shared chord scheme for the whole piece. Run from the Ngoma folder: python3 chords_patch.py [--sync]
Patches public/index.html, public/worp/index.html, tools/smoke.js and (with --sync) tools/sync_worp.py.
Every replace must match exactly once in each file it is meant for."""
import sys, os
ROOT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '.'
P = lambda x: os.path.join(ROOT, x)

def rep(path, pairs, optional=False):
    s = open(path).read()
    for a, b in pairs:
        n = s.count(a)
        if optional and n == 0:
            continue
        assert n == 1, (path, n, a[:90])
        s = s.replace(a, b)
    open(path, 'w').write(s)

# ---------- engine (the create() wrapper lives in sync_worp.py; Ngoma carries the generated copy) ----------
ENGINE = [
 ("get cx(){return host.cx?host.cx():.3}};",
  "get cx(){return host.cx?host.cx():.3},cdv:0};"),
 ("function startDrone(t){const o=state.deg|0;",
  "function startDrone(t){const o=(state.deg|0)+(state.cdv|0);"),
 ("polyOn('drone:'+i,state.key+36+semis(CUR.scale,d+(state.deg|0)),.8,t);return}",
  "polyOn('drone:'+i,state.key+36+semis(CUR.scale,d+(state.deg|0)+(state.cdv|0)),.8,t);return}"),
 ("{const R=host.rec,rs=host.res?host.res():4,",
  "state.cdv=host.cd?host.cd(g)|0:0;   /* v156: the line follows Ngoma's chords, one scale step per step of the chord root */\n        {const R=host.rec,rs=host.res?host.res():4,"),
 ("      if(!droneOn||t-lastT>1.5){",
  "      {const cd=host.cd?host.cd(g)|0:0;if(cd!==(state.cdv|0)){const o0=(state.deg|0)+(state.cdv|0);state.cdv=cd;   /* v156: Ngoma's chords. Only the voices whose note changes move; common tones hold */\n        if(droneOn)voicing.forEach((d,i)=>{const m0=state.key+36+semis(CUR.scale,d+o0),m=state.key+36+semis(CUR.scale,d+(state.deg|0)+cd);if(m!==m0)polyOn('drone:'+i,m,.8,t)})}}\n      if(!droneOn||t-lastT>1.5){"),
]
# the phrase player is copied from Worp itself
PHRASE = [("midi=state.key+48+semis(P.scale,e.deg+(state.deg|0)),",
           "midi=state.key+48+semis(P.scale,e.deg+(state.deg|0)+(state.cdv|0)),")]

CORE = r'''
/* v156 Chords (Jesse, 01-10: an automatic chord scheme for the whole piece). One harmony clock that every tonal layer follows:
   the pad (all types; Seasons keeps its voice leading, Loops picks chord tones), the Worp pad and lead (common tones hold) and
   Resonate. Chords come from the scale itself, so nothing you play on top can be wrong. Drone (the default) is Ngoma as before.
   A scheme is written in degrees of a seven-note scale (1 = the root) and lands on the nearest note of your scale; Auto picks one
   that suits the tradition. Seeded and counted from the start, so the export is the same as what you hear. */
const CH_PROGS=[['drone','Drone',null],['auto','Auto',null],['vamp','1 · 7',[1,7]],['onedrop','1 · 4',[1,4]],['kwela','1 · 4 · 1 · 5',[1,4,1,5]],
  ['montuno','1 · 4 · 5 · 4',[1,4,5,4]],['cadence','1 · 4 · 5 · 1',[1,4,5,1]],['andalus','1 · 7 · 6 · 5',[1,7,6,5]],['circle','1 · 6 · 3 · 7',[1,6,3,7]],['wander','Wander',null]];
const CH_AUTO={cuba:'montuno',west:'vamp',bra:'cadence',me:'andalus',car:'onedrop',saf:'kwela',ind:'drone',eur:'andalus',hyp:'drone',euc:'onedrop'};
const CH_BARS=[1,2,4], CHN=['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B'];
function chProgOf(){ let p=S.fx.chProg||'drone'; if(p==='auto') p=CH_AUTO[S.trad]||'drone'; return CH_PROGS.some(x=>x[0]===p)?p:'drone'; }
function chOn(){ return chProgOf()!=='drone'; }
function chPer(){ return (CH_BARS.includes(S.fx.chBars)?S.fx.chBars:2)*4*S.res; }
function chSemi(d){ const sc=padSc(), ref=sc.includes(3)&&!sc.includes(4)?[0,2,3,5,7,8,10]:[0,2,4,5,7,9,11]; return ref[(d-1)%7]; }
function chDegOf(st){ const sc=padSc(), n=sc.length; let best=0, bd=99; sc.forEach((x,i)=>{ const dd=Math.min(Math.abs(x-st),12-Math.abs(x-st)); if(dd<bd||(dd===bd&&x<st)){ bd=dd; best=i; } }); return best>n/2?best-n:best; }   // up to the fourth above, the rest below: the voicings stay near home
const CHW={k:'',list:[0]};
function chWander(k){ const key=[S.seed,S.scale].join(), n=padSc().length; if(CHW.k!==key){ CHW.k=key; CHW.list=[0]; }
  while(CHW.list.length<=k){ const i=CHW.list.length, q=j=>rnd(S.seed+1601,i,j), prev=CHW.list[i-1]; let d;
    if(i%4===0&&q(0)<.5) d=0; else { const mv=[3,-3,2,-2,4,-4,1,-1], w=[3,3,2.2,2.2,1.2,1.2,.5,.5]; let r=q(1)*w.reduce((a,b)=>a+b,0), m=3; for(let j=0;j<w.length;j++){ if((r-=w[j])<=0){ m=mv[j]; break; } } d=prev+m; }
    d=((d%n)+n)%n; if(d>n/2) d-=n; if(d===prev) d=prev?0:(n>5?3:2); CHW.list.push(d); }   // home every four changes now and then, never the same chord twice
  return CHW.list[k]; }
function chordAt(g){ const p=chProgOf(); if(p==='drone') return 0; const k=Math.floor(Math.max(0,g)/chPer());
  if(p==='wander') return chWander(k); const L=CH_PROGS.find(x=>x[0]===p)[2]; return chDegOf(chSemi(L[k%L.length])); }
function chName(d){ const sc=padSc(), n=sc.length, r=sc[((d%n)+n)%n], has=x=>sc.includes((r+x)%12);
  return CHN[(S.key+r)%12]+(has(4)&&has(7)?'':has(3)&&has(7)?'m':has(3)&&has(6)?'dim':has(5)?'sus4':has(2)?'sus2':'5'); }
function chKey(){ return chProgOf()+'/'+chPer(); }
function chLabel(){ if(!chOn()) return 'ンゴマ'; const per=chPer();
  if(playing){ const g=Math.max(0,gStep); return chName(chordAt(g))+'  →  '+chName(chordAt(g+per)); }
  const p=chProgOf(), L=p==='wander'?4:CH_PROGS.find(x=>x[0]===p)[2].length; return Array.from({length:L},(_,k)=>chName(chordAt(k*per))).join(' · '); }
'''

UI_HTML = ('      <label class="field"><span class="lbl">Scale</span><select id="scale"></select></label>\n',
           '      <label class="field"><span class="lbl">Scale</span><select id="scale"></select></label>\n'
           '      <label class="field" title="Chords for the whole piece. The pad, the Worp pad and lead and Resonate follow them; the drums stay in the key. Drone: no changes, Ngoma as before. Auto: a scheme that suits the tradition. Every chord comes from your scale"><span class="lbl">Chords</span><select id="chprog"></select></label>\n'
           '      <label class="field" title="How long each chord lasts. Export a loop at least as long as the scheme to get all of it"><span class="lbl">Per</span><select id="chbars"><option value="1">1 bar</option><option value="2">2 bars</option><option value="4">4 bars</option></select></label>\n')

INIT = ("  key.value=S.key; key.onchange=()=>{ S.key=+key.value; save(); };",
        "  key.value=S.key; key.onchange=()=>{ S.key=+key.value; save(); };\n"
        "  { const cp=$('chprog'), cb=$('chbars');   /* v156 Chords */\n"
        "    const fill=()=>{ const au=CH_AUTO[S.trad]||'drone', an=(CH_PROGS.find(x=>x[0]===au)||CH_PROGS[0])[1]; cp.textContent=''; CH_PROGS.forEach(([v,l])=>{ const o=document.createElement('option'); o.value=v; o.textContent=v==='auto'?'Auto ('+an+')':l; cp.append(o); }); cp.value=S.fx.chProg||'drone'; cb.value=String(CH_BARS.includes(S.fx.chBars)?S.fx.chBars:2); };\n"
        "    fill(); UPD.push(fill);\n"
        "    cp.onchange=()=>{ S.fx.chProg=cp.value; save(); mstatus(chOn()?'Chords: '+chLabel()+'. The pad, Worp and Resonate follow from the next change.':'Chords off: one drone, as before.'); };\n"
        "    cb.onchange=()=>{ S.fx.chBars=+cb.value; save(); }; }")

def main():
    idx, worp, smoke = P('public/index.html'), P('public/worp/index.html'), P('tools/smoke.js')
    rep(idx, ENGINE + PHRASE + [
     ("fEnv:.3,fEnvSrc:'mix',fLfo:.12,fRate:0,", "fEnv:.3,fEnvSrc:'mix',fLfo:.12,fRate:0,chProg:'drone',chBars:2,"),
     ("const padNt=(root,d)=>{ const sc=padSc(), n=sc.length; return root+sc[((d%n)+n)%n]+12*Math.floor(d/n); };",
      "const padNt=(root,d)=>{ const sc=padSc(), n=sc.length; return root+sc[((d%n)+n)%n]+12*Math.floor(d/n); };" + CORE),
     # pad followers
     ("step=Math.round(prog[bar%prog.length]*n/7);   // steps are written for 7-note scales",
      "step=chOn()?chordAt(g):Math.round(prog[bar%prog.length]*n/7);   // steps are written for 7-note scales; v156 with Chords on, the chord root"),
     ("function seasonChord(c){ const sc=(SCALES[S.scale]||SCALES.mpenta).iv, n=sc.length, key=[S.seed,S.scale,S.key].join();",
      "function seasonChord(c){ const sc=(SCALES[S.scale]||SCALES.mpenta).iv, n=sc.length, key=[S.seed,S.scale,S.key,chKey(),S.res].join();"),
     ("deg=prev.deg+m; if(Math.abs(deg)>n) deg-=Math.sign(deg)*n; }",
      "deg=prev.deg+m; if(Math.abs(deg)>n) deg-=Math.sign(deg)*n; }\n    if(chOn()) deg=chordAt(i*8*S.res);   /* v156: the scheme picks the chord, Seasons keeps its voice leading */"),
     ("hz=pmtof(padNt(root,M.v[k]));", "hz=pmtof(padNt(root,M.v[k]+chordAt(g)));"),
     ("hz=pmtof(padNt(root,M.d[i])),", "hz=pmtof(padNt(root,M.d[i]+chordAt(g))),"),
     ("const deg=Math.floor(q(k,3)*n)+(k===0?-n:0), second=q(k,4)<.55,",
      "const deg=(chOn()?chordAt(g)+[0,2,4][Math.floor(q(k,3)*3)]:Math.floor(q(k,3)*n))+(k===0?-n:0), second=q(k,4)<.55,"),
     # Resonate
     ("r=k?sc[degs[Math.floor(rnd(S.seed+461,k,1)*degs.length)]]:0; }",
      "r=k?sc[degs[Math.floor(rnd(S.seed+461,k,1)*degs.length)]]:0; }\n  if(chOn()){ const d=chordAt(g); r=sc[((d%n)+n)%n]; }   /* v156: the chord root of the scheme; the type keeps its shape */"),
     ("if(!R||!R.res||!(R.ra>0)||S.fx.mgChord!=='wander') return; const BL=4*S.res; if(g%(2*BL)) return;",
      "if(!R||!R.res||!(R.ra>0)||(S.fx.mgChord!=='wander'&&!chOn())) return; const BL=4*S.res; if(g%(chOn()?chPer():2*BL)) return;"),
     # Worp engines get the clock
     ("if(!G.worp) G.worp=WorpEngine.create(ctx,P.bus,{key:()=>S.key,", "if(!G.worp) G.worp=WorpEngine.create(ctx,P.bus,{cd:g=>chordAt(g),key:()=>S.key,"),
     ("if(!G.wlead) G.wlead=WorpEngine.create(ctx,G.lead.bus,{kind:'lead',", "if(!G.wlead) G.wlead=WorpEngine.create(ctx,G.lead.bus,{kind:'lead',cd:g=>chordAt(g),"),
     ("const E=WorpEngine.create(oc,bus,{kind:'lead',", "const E=WorpEngine.create(oc,bus,{kind:'lead',cd:g=>chordAt(g),"),
     # display and UI
     ('<span class="sc-l sc-tr">ンゴマ</span>', '<span class="sc-l sc-tr" id="scch">ンゴマ</span>'),
     ("  const lb=$('scbpm'); if(lb){ const t=Math.round(S.bpm)+' BPM'; if(lb.textContent!==t) lb.textContent=t; }",
      "  const lb=$('scbpm'); if(lb){ const t=Math.round(S.bpm)+' BPM'; if(lb.textContent!==t) lb.textContent=t; }\n  { const ch=$('scch'); if(ch){ const t=chLabel(); if(ch.textContent!==t) ch.textContent=t; } }   /* v156: the chord now and the next one */"),
     UI_HTML, INIT,
     ("    <dt>Pad</dt>", "    <dt>Chords</dt><dd>Next to Key and Scale. One chord scheme for the whole piece: the pad (every type), the Worp pad and lead and Resonate follow it, the drums stay in the key. <i>Drone</i> is Ngoma as it was: no changes. <i>Auto</i> picks a scheme that suits the tradition (Afro-Cuban 1 · 4 · 5 · 4, Caribbean 1 · 4, Middle Eastern and Southern Europe 1 · 7 · 6 · 5, North Indian stays on the drone). <i>Wander</i> finds its own way home. <i>Per</i> sets how long a chord lasts. Every chord is built from your scale, so whatever you play on top still fits. The scope shows the chord now and the next one. Export a loop at least as long as the scheme to get all of it.</dd>\n    <dt>Pad</dt>"),
    ])
    rep(worp, PHRASE)
    rep(smoke, [("  await p.close();   /* else Worp links to this Ngoma tab and plays there */",
     "  await check('Chords: Drone changes nothing, a scheme moves the pad', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj);\n"
     "      const keep = JSON.stringify(S.fx); S.bars = 4; S.fx.padOn = true; S.fx.padLvl = .5; S.fx.padType = 0; S.fx.chBars = 1; S.renderOnly = -1;\n"
     "      S.fx.chProg = 'drone'; const d0 = [0, 16, 32, 48].map(g => chordAt(g)); const a = await renderLoop(false, 22050);\n"
     "      S.fx.chProg = 'montuno'; const d1 = [0, 16, 32, 48].map(g => chordAt(g)), names = d1.map(chName); const b = await renderLoop(false, 22050);\n"
     "      S.fx.chProg = 'wander'; const w1 = [0, 1, 2, 3, 4, 5].map(k => chordAt(k * 16)), w2 = [0, 1, 2, 3, 4, 5].map(k => chordAt(k * 16));\n"
     "      let diff = 0; for (let i = 0; i < a[0].length; i += 7) diff += Math.abs(a[0][i] - b[0][i]);\n"
     "      S.renderOnly = null; Object.assign(S.fx, JSON.parse(keep)); return { d0, d1, names, ra: rms(a[0]), rb: rms(b[0]), diff, w: w1.join() === w2.join() && new Set(w1).size > 1 }; }, rmsJS);\n"
     "    assert(r.d0.every(x => x === 0), 'drone moved ' + r.d0); assert(new Set(r.d1).size >= 3, 'scheme flat ' + r.d1); assert(r.ra > .0005 && r.rb > .0005, 'silent');\n"
     "    assert(r.diff > 1, 'the pad did not follow'); assert(r.w, 'wander not seeded'); return r.names.join(' ') + ', wander seeded'; });\n\n"
     "  await p.close();   /* else Worp links to this Ngoma tab and plays there */")])
    if '--sync' in sys.argv:
        rep(P('tools/sync_worp.py'), ENGINE, optional=True)
    print('ok')

if __name__ == '__main__':
    main()
