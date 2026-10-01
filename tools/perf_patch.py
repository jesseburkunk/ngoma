#!/usr/bin/env python3
"""v163 performance: Worp convolvers on demand, filter bypass, longer lookahead, Stable playback, a load warning, a smoke budget.
Run from the Ngoma folder, then tools/sync_worp.py."""
def rep(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, s.count(a), a[:80])
        s = s.replace(a, b)
    open(path, 'w').write(s)

# 1. Worp: one convolver per room actually used (it was three long ones, always running), in Worp itself; sync copies it to Ngoma
rep('public/worp/index.html', [
 ("  A.revs=ROOMS.map(rm=>{const c=C.createConvolver();c.buffer=makeIR(rm.s);const s=C.createGain();s.gain.value=0;A.post.connect(s);s.connect(c);c.connect(A.wetR);return s});",
  "  A.revs=ROOMS.map(rm=>{const s=C.createGain();s.gain.value=0;A.post.connect(s);return s});A.revC=[];   // v1.24 (Ngoma v163): the convolver of a room is made the first time a patch uses it, so one long reverb runs instead of three"),
 ("  A.revs.forEach((s,i)=>s.gain.setTargetAtTime(i===P.fx.room?P.fx.rev:0,t,.4));",
  "  {const r=P.fx.room|0;if(!A.revC[r]&&ROOMS[r]){const c=A.post.context.createConvolver();c.buffer=makeIR(ROOMS[r].s);A.revs[r].connect(c);c.connect(A.wetR);A.revC[r]=c}}\n  A.revs.forEach((s,i)=>s.gain.setTargetAtTime(i===P.fx.room?P.fx.rev:0,t,.4));"),
])

rep('public/index.html', [
 # 2. the filter worklet passes the sound straight through when it would do nothing (fully open, no resonance, drive or movement)
 ("    const sc=ins[1], mod={env:p.env[0],lfo:p.lfo[0],per:p.per[0],t0:p.t0[0],t:currentTime,det:(p.sc[0]>.5)?((sc&&sc.length)?sc:[]):null};\n    this.f.process(",
  "    const sc=ins[1], mod={env:p.env[0],lfo:p.lfo[0],per:p.per[0],t0:p.t0[0],t:currentTime,det:(p.sc[0]>.5)?((sc&&sc.length)?sc:[]):null};\n"
  "    if(p.cutoff[0]>=19500&&p.res[0]<.001&&p.drive[0]<.001&&Math.round(p.model[0])===0&&mod.env<=.001&&mod.lfo<=.001){ for(let c=0;c<o.length;c++){ const x=i[c]||i[0]; o[c].set(x.length===o[c].length?x:o[c].fill(0)); } this.idle=true; return true; }   /* v163: open and still = a wire (Clean only: the other models colour even when open) */\n"
  "    if(this.idle){ this.idle=false; this.f=new NgomaFilterCore(sampleRate); }\n    this.f.process("),
 # 3. lookahead and Stable playback
 ("  while(nextT < actx.currentTime+.12){", "  while(nextT < actx.currentTime+(STABLE?.3:.2)){   /* v163: 0.2 s ahead (was 0.12), 0.3 s in Stable */"),
 ("function tick(){ const sd=stepDur(S); if(nextT<actx.currentTime-.05){ const k=Math.ceil((actx.currentTime-nextT)/sd); gStep+=k; nextT+=k*sd; }",
  "function tick(){ const sd=stepDur(S); if(nextT<actx.currentTime-.05){ const k=Math.ceil((actx.currentTime-nextT)/sd); gStep+=k; nextT+=k*sd; loadLate(); }"),
 ("function ensureCtx(){ if(!actx){ const AC=window.AudioContext||window.webkitAudioContext; if(M4L.on&&M4L.sr>0){ try{ actx=new AC({sampleRate:M4L.sr}); }catch(e){ actx=new AC(); } } else actx=new AC();",
  "/* v163 Stable playback (Jesse: on a MacBook Air the sound locks up, the Mac mini is fine): a larger audio buffer and a longer look-ahead, at the\n"
  "   cost of a little more delay on MIDI keys. Kept per computer. loadLate: the planner found itself late (the page was blocked for a moment), so\n"
  "   a few steps were skipped; the scope shows LATE for a few seconds and the first time Ngoma suggests Stable. */\n"
  "var STABLE=(()=>{ try{ return localStorage.getItem('ngoma.stable')==='1'; }catch(e){ return false; } })(), LATE={n:0,t:0,told:false};\n"
  "function loadLate(){ LATE.n++; LATE.t=performance.now(); if(!LATE.told&&!STABLE&&LATE.n>=3){ LATE.told=true; status('Ngoma could not keep up for a moment. If the sound stutters, switch on Stable next to Volume.'); } }\n"
  "function stableSet(on){ STABLE=!!on; try{ localStorage.setItem('ngoma.stable',STABLE?'1':'0'); }catch(e){} const b=$('stablebtn'); if(b) b.setAttribute('aria-pressed',STABLE?'true':'false');\n"
  "  if(actx){ const was=playing; if(playing) stop(); clearTimeout(suspT); try{ actx.close(); }catch(e){} actx=null; AG=null; if(was) setTimeout(start,120); }\n"
  "  status(STABLE?'Stable playback on: a bigger audio buffer, a little more delay on MIDI keys.':'Stable playback off: the shortest delay.'); }\n"
  "function ensureCtx(){ if(!actx){ const AC=window.AudioContext||window.webkitAudioContext, LH=STABLE?{latencyHint:'playback'}:{}; if(M4L.on&&M4L.sr>0){ try{ actx=new AC({...LH,sampleRate:M4L.sr}); }catch(e){ actx=new AC(); } } else { try{ actx=new AC(LH); }catch(e){ actx=new AC(); } }"),
 ('      <div class="tgrp tmix">',
  '      <div class="tgrp tmix"><button class="tg" id="stablebtn" type="button" aria-pressed="false" title="Stable playback: a bigger audio buffer and a longer look-ahead, for a laptop where the sound stutters. MIDI keys get a little more delay. Kept on this computer">Stable</button>'),
 ("  key.value=S.key; key.onchange=()=>{ S.key=+key.value; save(); };",
  "  key.value=S.key; key.onchange=()=>{ S.key=+key.value; save(); };\n  { const sb=$('stablebtn'); if(sb){ sb.setAttribute('aria-pressed',STABLE?'true':'false'); sb.onclick=()=>stableSet(!STABLE); } }"),
 ("  { const ch=$('scch'); if(ch){ const t=chLabel(); if(ch.textContent!==t) ch.textContent=t; } }",
  "  { const ch=$('scch'); if(ch){ const t=chLabel(); if(ch.textContent!==t) ch.textContent=t; } }\n  { const br=document.querySelector('.sc-br'); if(br){ const late=performance.now()-LATE.t<4000&&LATE.n>0, t=late?'LATE':'MIX'; if(br.textContent!==t){ br.textContent=t; br.style.color=late?'var(--accent)':''; } } }   /* v163 */"),
 ("    <dt>Volume</dt><dd>Master volume for listening, at the end of the scenes line.",
  "    <dt>Stable</dt><dd>Next to Volume. For a laptop where the sound stutters: a bigger audio buffer and a longer look-ahead, at the cost of a little more delay on MIDI keys. When the scope shows <i>LATE</i>, Ngoma could not keep up for a moment.</dd>\n    <dt>Volume</dt><dd>Master volume for listening, at the end of the scenes line."),
])

# 5. smoke: a load budget, relative to the drums alone, so it holds on any computer
rep('tools/smoke.js', [
 ("  await check('Bloom: renders,",
  "  await check('Load budget: layers do not cost more than they should', async () => { const r = await p.evaluate(async () => { const keep = JSON.stringify(S.fx), b0 = S.bars; S.bars = 2;\n"
  "      const t = async fn => { Object.assign(S.fx, JSON.parse(keep)); fn && fn(); let best = 1e9; for (let k = 0; k < 2; k++) { const t0 = performance.now(); await renderLoop(false, 48000); best = Math.min(best, performance.now() - t0); } return best; };\n"
  "      const d = await t(), all = await t(() => { S.fx.padOn = true; S.fx.padType = 7; S.fx.leadOn = true; S.fx.mgOn = true; S.fx.mgMode = 1; S.fx.rvType = 'bloom'; S.fx.rvLevel = .3; });\n"
  "      Object.assign(S.fx, JSON.parse(keep)); S.bars = b0; return { d, all, x: all / d, rt: d / 1000 / (2 * 4 * 60 / S.bpm) }; });\n"
  "    assert(r.x < 3.3, 'everything on costs ' + r.x.toFixed(2) + ' x the drums alone (budget 3.3)'); return 'all on ' + r.x.toFixed(2) + ' x drums, drums ' + r.rt.toFixed(2) + ' x real time here'; });\n\n"
  "  await check('Bloom: renders,"),
])
print('ok')
