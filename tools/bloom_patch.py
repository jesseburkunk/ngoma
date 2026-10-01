#!/usr/bin/env python3
"""v161 Bloom: a reverb type whose tail blooms into the chord. Run from the Ngoma folder."""
p = 'public/index.html'
s = open(p).read()

SHIM = r'''registerProcessor('ngoma-comb',NgomaCombProc);
// v161 Bloom: an octave-up pitch shifter for the reverb's feedback loop. Two read heads half a window apart run through a delay line
// at twice the speed and cross-fade with a sine window, so every pass through the loop climbs an octave, like a shimmer reverb.
class NgomaShimProc extends AudioWorkletProcessor{ constructor(){ super(); this.N=16384; this.b=[new Float32Array(this.N),new Float32Array(this.N)]; this.w=0; this.p=0; this.W=Math.round(sampleRate*.09); }
  process(ins,outs){ const i=ins[0], o=outs[0]; if(!o||!o.length) return true; const n=o[0].length, N=this.N, W=this.W, st=1/W; let w=this.w, p=this.p;
    for(let c=0;c<2;c++){ const src=i&&i.length?(i[c]||i[0]):null, buf=this.b[c], out=o[c]; if(!out) continue; w=this.w; p=this.p;
      for(let k=0;k<n;k++){ buf[w]=src?src[k]:0; let y=0;
        for(let h=0;h<2;h++){ const ph=(p+h*.5)%1, d=2+W*(1-ph), r=w-d, r0=Math.floor(r), f=r-r0, a=buf[((r0%N)+N)%N], b2=buf[(((r0+1)%N)+N)%N]; y+=(a+(b2-a)*f)*Math.sin(Math.PI*ph); }
        out[k]=y*.7; w=(w+1)%N; p+=st; if(p>=1) p-=1; } }
    this.w=w; this.p=p; return true; } }
registerProcessor('ngoma-shim',NgomaShimProc);'''

R = [
 ("registerProcessor('ngoma-comb',NgomaCombProc);", SHIM),
 ("  spring:{name:'Spring', rt:2.2, er:0, size:1, bright:.55},   // v89: a two-spring tank, as in tape echoes and dub\n",
  "  spring:{name:'Spring', rt:2.2, er:0, size:1, bright:.55},   // v89: a two-spring tank, as in tape echoes and dub\n"
  "  bloom:{name:'Bloom', rt:4, er:0, size:1.6, bright:.6},      // v161: a long tail that climbs an octave each pass and rings on the chord\n"),
 ("  inp.connect(pre).connect(hp).connect(lp).connect(conv).connect(ret).connect(out);\n  return {in:inp,pre,hp,lp,conv,ret,key:''};\n}",
  "  inp.connect(pre).connect(hp).connect(lp).connect(conv).connect(ret).connect(out);\n"
  "  /* v161 Bloom (Jesse: more effects like Resonate that add so much; the sound of Barker). Two extra paths that stay silent unless the\n"
  "     type is Bloom: a feedback loop through an octave-up shifter (shimmer), and four narrow band-passes on the tones of the current chord,\n"
  "     so the tail does not just wash but sings the chord. The shifter is made once the worklet is loaded (bloomSync). */\n"
  "  const B={fb:ctx.createGain(),dly:ctx.createDelay(.1),lo:bq(ctx,'highpass',500,.5),hi:bq(ctx,'lowpass',5200,.5),bank:ctx.createGain(),bp:[],sh:null};\n"
  "  B.fb.gain.value=0; B.bank.gain.value=0; B.dly.delayTime.value=.03; B.lo.connect(B.hi).connect(B.fb).connect(B.dly).connect(lp);\n"
  "  for(let k=0;k<4;k++){ const f=bq(ctx,'bandpass',440,16); conv.connect(f); f.connect(B.bank); B.bp.push(f); } B.bank.connect(ret);\n"
  "  return {in:inp,pre,hp,lp,conv,ret,key:'',B};\n}\n"
  "function bloomOn(G){ const F=S.fx; return !!(G&&G.rv&&G.rv.B&&F.rvOn&&F.rvType==='bloom'&&!G.dry); }\n"
  "function bloomHz(g){ const sc=padSc(), n=sc.length, d=chordAt(g); return [d,d+2,d+4,d+n].map(x=>{ let f=mtof(60+S.key+sc[((x%n)+n)%n]+12*Math.floor(x/n)); while(f>1400) f/=2; while(f<330) f*=2; return f; }); }\n"
  "function bloomSync(G){ const B=G&&G.rv&&G.rv.B; if(!B) return; const c=G.ctx, on=bloomOn(G);\n"
  "  if(on&&!B.sh&&c._fok){ try{ B.sh=new AudioWorkletNode(c,'ngoma-shim',{numberOfInputs:1,numberOfOutputs:1,outputChannelCount:[2]}); G.rv.conv.connect(B.sh); B.sh.connect(B.lo); }catch(e){ B.sh=null; } }\n"
  "  pv(G,B.fb.gain,on&&B.sh?.36:0); pv(G,B.bank.gain,on?1.1:0); if(on){ const hz=bloomHz(0); B.bp.forEach((f,k)=>{ f.frequency.value=hz[k]; }); } }\n"
  "function bloomStep(G,g,t){ if(!bloomOn(G)||g%(4*S.res)) return; const hz=bloomHz(g), B=G.rv.B, now=Math.max(G.ctx.currentTime||0,t); B.bp.forEach((f,k)=>f.frequency.setTargetAtTime(hz[k],now,.35)); }   /* the bank glides to the new chord over about a second */"),
 ("  padBar(ctx,G,g,t); leadBar(ctx,G,g,t);\n  if(G.mg && g%(S.bars*4*S.res)===0) magicSync(G);",
  "  padBar(ctx,G,g,t); leadBar(ctx,G,g,t); bloomStep(G,g,t);\n  if(G.mg && g%(S.bars*4*S.res)===0) magicSync(G);"),
 ("G.rv.conv.buffer=makeIR(c.sampleRate); G.rv.key=k; }",
  "G.rv.conv.buffer=makeIR(c.sampleRate); G.rv.key=k; }\n  bloomSync(G);"),
 ("  if(F.rvOn) t+=(RV_TYPES[F.rvType]||RV_TYPES.room).rt*F.rvSize*1.3;",
  "  if(F.rvOn) t+=(RV_TYPES[F.rvType]||RV_TYPES.room).rt*F.rvSize*1.3;\n  if(F.rvOn&&F.rvType==='bloom') t+=4;   /* v161: the shimmer keeps climbing a while */"),
 ("<dt>Reverb</dt><dd>Room, Plate, Hall, Cave and Spring, with length, pre-delay, tone and return. The low end stays out.",
  "<dt>Reverb</dt><dd>Room, Plate, Hall, Cave, Spring and Bloom, with length, pre-delay, tone and return. The low end stays out. <i>Bloom</i> lets every hit open up into the chord.<details class=\"g-more\"><summary>About Bloom</summary>A long tail that climbs an octave with every pass, like a shimmer reverb, and rings on the tones of the current chord, so the drums turn into a soft chord that swells and fades. It follows <i>Chords</i>; on Drone it rings on the root chord of your key. Works well with Resonate, and with Return around 20 to 40%.</details>"),
]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
open(p, 'w').write(s)

q = 'tools/smoke.js'; t = open(q).read()
a = "  await p.close();   /* else Worp links to this Ngoma tab and plays there */"
assert t.count(a) == 1
t = t.replace(a, "  await check('Bloom: renders, the tail sings and stays in bounds', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), keep = JSON.stringify(S.fx); S.bars = 2;\n"
 "      Object.assign(S.fx, { rvOn: true, rvType: 'hall', rvLevel: .5 }); const a = await renderLoop(false, 22050); S.fx.rvType = 'bloom'; const b = await renderLoop(false, 22050);\n"
 "      let pk = 0; for (const v of b[0]) pk = Math.max(pk, Math.abs(v)); const hz = bloomHz(0); Object.assign(S.fx, JSON.parse(keep)); return { ra: rms(a[0]), rb: rms(b[0]), pk, hz }; }, rmsJS);\n"
 "    assert(r.rb > 0 && r.ra > 0, 'silent or not finite'); assert(r.pk <= 1.001, 'peak ' + r.pk); assert(r.hz.every(f => f >= 330 && f <= 1400), 'bank ' + r.hz);\n"
 "    return 'bank ' + r.hz.map(Math.round).join('/') + ' Hz'; });\n\n" + a)
open(q, 'w').write(t)
print('ok')
