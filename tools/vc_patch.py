#!/usr/bin/env python3
"""v163 voice cache: live drum hits play from pre-rendered buffers. Run from the Ngoma folder."""
def rep(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, s.count(a), a[:80])
        s = s.replace(a, b)
    open(path, 'w').write(s)

OLD_SWITCH = """  if(I.gain){ const tg=ctx.createGain(); tg.gain.value=I.gain; tg.connect(out); out=tg; }   // per-voice trim (tumba: Jesse found it too dominant, -3.5 dB)
  if(I.kind==='mem'){ let p=ARTP[I.tbl][I.arts[a]]||ARTP[I.tbl][I.arts[0]];
    if(p.slapIv){ const m=I.base+L.tune+tn+(S.fx.kitPitch||0), d=[3,4,5,2].find(x=>inScale(m+x,S.key)) ?? 3; p={...p,pm:Math.pow(2,d/12)}; }   // the slap rings a third or so above the open tone: pick the one in your scale
    vMem(ctx,out,t,v,hz,T,p,rv,tv); }
  else if(I.kind==='bell') vBell(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='wood') vWood(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='udu') vUdu(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='tri') vTri(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='tabla') vTabla(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='bayan') vBayan(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='jng') vTamb(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='clap') vClap(ctx,out,t,v,hz,T,a,rv,tv);
  else vShk(ctx,out,t,v,hz,T,acc,rv,tv);
}
"""
NEW_SWITCH = """  voiceKind(ctx,out,I,a,t,v,acc,rv,I.base+L.tune+tn+(S.fx.kitPitch||0),hz,T,tv);
}
function voiceKind(ctx,out,I,a,t,v,acc,rv,m,hz,T,tv){
  if(I.gain){ const tg=ctx.createGain(); tg.gain.value=I.gain; tg.connect(out); out=tg; }   // per-voice trim (tumba: Jesse found it too dominant, -3.5 dB)
  if(I.kind==='mem'){ let p=ARTP[I.tbl][I.arts[a]]||ARTP[I.tbl][I.arts[0]];
    if(p.slapIv){ const d=[3,4,5,2].find(x=>inScale(m+x,S.key)) ?? 3; p={...p,pm:Math.pow(2,d/12)}; }   // the slap rings a third or so above the open tone: pick the one in your scale
    vMem(ctx,out,t,v,hz,T,p,rv,tv); }
  else if(I.kind==='bell') vBell(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='wood') vWood(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='udu') vUdu(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='tri') vTri(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='tabla') vTabla(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='bayan') vBayan(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='jng') vTamb(ctx,out,t,v,hz,T,a,rv,tv);
  else if(I.kind==='clap') vClap(ctx,out,t,v,hz,T,a,rv,tv);
  else vShk(ctx,out,t,v,hz,T,acc,rv,tv);
}
/* v163 voice cache (Jesse: the sound locks up on a MacBook Air). Every live drum hit used to build about twenty audio nodes; now a hit plays
   from a buffer that was rendered once with exactly the same synthesis: one source and one gain. A buffer is made per instrument, stroke,
   note, length, three velocity layers and three seeded variations of the stroke (plus colour), so hits still differ the way real strokes do;
   the exact velocity is the gain, Drift's pitch is the detune. The first hit of something new is synthesised as before while its buffer is
   rendered in the background. Exports keep synthesising every hit, so they stay exactly as they were. */
const VC={map:new Map(),q:[],pend:new Set(),busy:false,sr:0,on:true,hit:0,miss:0};
const VCR=[[-.55,.1,.45],[.35,-.4,-.2],[.05,.55,-.6]], VCL=[.25,.55,1];
function vcSpec(i,a,t,v,acc,rv,tn,dc){ const I=INSTR[i], L=S.lanes[i]; if(!I||!L) return null; const dr=driftAt(i,t), tv=L.tvar??.45;
  const mf=I.base+L.tune+tn+(S.fx.kitPitch||0), m=Math.round(mf); if(Math.abs(mf-m)>.01) return null;   /* a fractional tune is synthesised */
  const T0=I.dec*L.decay*dc*(dr?dr.d:1), T=Math.pow(2,Math.round(Math.log2(Math.max(.01,T0))*8)/8);   /* lengths in steps of about 9% */
  const vl=v>.75?1:v>.36?.55:.25, r=rv||[0,0,0], k=Math.floor(((r[0]+1)*2.9+(r[2]+1)*1.7))%3, e=Math.round(((L.col||0)*.9+(dr?dr.e:0))/.3)*.3;
  const p=I.kind==='mem'?(ARTP[I.tbl][I.arts[a]]||{}):{};
  const key=[i,a,m,T.toFixed(4),vl,k,e.toFixed(1),tv.toFixed(2),(S.fat||0).toFixed(2),I.kind==='shk'?(acc?1:0):'',p.slapIv?S.key:''].join('|');
  return {key,i,a,m,T,vl,k,e,tv,acc,g:v/vl*(dr?dr.l:1),cents:dr?dr.c:0}; }
function vcGet(sp,sr){ if(VC.sr!==sr){ VC.sr=sr; VC.map.clear(); VC.q.length=0; VC.pend.clear(); }
  const b=VC.map.get(sp.key); if(b){ VC.map.delete(sp.key); VC.map.set(sp.key,b); return b; }
  if(!VC.pend.has(sp.key)&&VC.q.length<64){ VC.pend.add(sp.key); VC.q.push(sp); vcPump(); } return null; }
async function vcPump(){ if(VC.busy) return; VC.busy=true;
  try{ while(VC.q.length){ const sp=VC.q.shift(), sr=VC.sr, I=INSTR[sp.i], len=Math.min(6,sp.T*2.2+.3);
      try{ const oc=new OfflineAudioContext(1,Math.ceil(len*sr),sr), rv=[VCR[sp.k][0],Math.max(-1,Math.min(1,VCR[sp.k][1]+sp.e)),VCR[sp.k][2]];
        voiceKind(oc,oc.destination,I,sp.a,0,sp.vl,sp.acc,rv,sp.m,mtof(sp.m),sp.T,sp.tv);
        let buf=await oc.startRendering(); const d=buf.getChannelData(0); let n=d.length; while(n>256&&Math.abs(d[n-1])<1e-5) n--;   /* trim the silent end */
        if(n<d.length-256){ const b2=new AudioBuffer({numberOfChannels:1,length:n+64,sampleRate:sr}); b2.copyToChannel(d.subarray(0,n+64),0); buf=b2; }
        if(sr===VC.sr){ VC.map.set(sp.key,buf); while(VC.map.size>400) VC.map.delete(VC.map.keys().next().value); } }catch(e){}
      VC.pend.delete(sp.key); await new Promise(r=>setTimeout(r,0)); } }
  finally{ VC.busy=false; } }
"""

rep('public/index.html', [
 (OLD_SWITCH, NEW_SWITCH),
 ("  const I=INSTR[i], L=S.lanes[i], dr=driftAt(i,t), tv=L.tvar??.45;\n  out=chokeIn(ctx,out,i,t);\n",
  "  out=chokeIn(ctx,out,i,t);\n"
  "  if(ctx===actx&&VC.on){ const sp=vcSpec(i,a,t,v,acc,rv,tn,dc); if(sp){ const buf=vcGet(sp,ctx.sampleRate); if(buf){ const s=ctx.createBufferSource(), g=ctx.createGain(); s.buffer=buf; if(sp.cents) s.detune.value=sp.cents; g.gain.value=sp.g; s.connect(g).connect(out); s.start(t); VC.hit++; return; } VC.miss++; } }   /* v163: from the voice cache */\n"
  "  const I=INSTR[i], L=S.lanes[i], dr=driftAt(i,t), tv=L.tvar??.45;\n"),
])

rep('tools/smoke.js', [
 ("  await check('Load budget:",
  "  await check('Voice cache: live hits play from buffers that sound like the synthesis', async () => { const r = await p.evaluate(async () => {\n"
  "      const i = INSTR.findIndex(x => x.id === 'conga'), sp = vcSpec(i, 0, 0, 1, true, [.1, .2, .3], 0, 1); if (!sp) return { err: 'no spec' };\n"
  "      ensureCtx(); const sr = actx.sampleRate; vcGet(sp, sr); for (let k = 0; k < 60 && !VC.map.get(sp.key); k++) await new Promise(r => setTimeout(r, 50));\n"
  "      const buf = VC.map.get(sp.key); if (!buf) return { err: 'not rendered' }; const oc = new OfflineAudioContext(1, Math.ceil(sr * 1.2), sr);\n"
  "      voiceKind(oc, oc.destination, INSTR[i], 0, 0, sp.vl, true, [VCR[sp.k][0], Math.max(-1, Math.min(1, VCR[sp.k][1] + sp.e)), VCR[sp.k][2]], sp.m, mtof(sp.m), sp.T, sp.tv); const ref = await oc.startRendering();\n"
  "      const rms = a => { let s = 0; for (const v of a) s += v * v; return Math.sqrt(s / a.length); }, n = Math.min(buf.length, ref.length), A = buf.getChannelData(0).subarray(0, n), B = ref.getChannelData(0).subarray(0, n);\n"
  "      const db = 20 * Math.log10(rms(A) / rms(B)); start(); await new Promise(r => setTimeout(r, 4000)); const o = { db, hit: VC.hit, miss: VC.miss, size: VC.map.size }; stop(); return o; });\n"
  "    assert(!r.err, r.err); assert(Math.abs(r.db) < 1.5, 'cached hit differs ' + r.db.toFixed(2) + ' dB'); assert(r.hit > 0, 'no hits from the cache (' + r.miss + ' misses)');\n"
  "    return r.hit + ' hits from ' + r.size + ' buffers, ' + r.miss + ' synthesised while filling'; });\n\n"
  "  await check('Load budget:"),
])
print('ok')
