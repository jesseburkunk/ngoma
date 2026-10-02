import re
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__))
w=open(os.path.join(HERE,'..','public','worp','index.html')).read()
js=re.search(r'<script>(.*)</script>',w,re.S).group(1)
def cut(a,b):
    i=js.index(a); j=js.index(b,i); return js[i:j]
gen=cut("const NN=","/* ---------- master filter")
gen=gen.replace("function uniqueName(P){if(typeof state==='undefined')return;","function uniqueName(P){return;")
init=cut("function makeIR(sec){","function prepWaves(P){")
run=cut("function prepWaves(P){","/* live playing")
# ---- engine-specific init
init=init.replace("function initAudio(){\n  if(ctx){if(ctx.state!=='running')ctx.resume();return}\n  ctx=new (window.AudioContext||window.webkitAudioContext)({latencyHint:'interactive'});\n  const C=ctx;","function initGraph(){\n  const C=ctx;")
init=init.replace("A.master.gain.value=+$('#vol').value;","A.master.gain.value=.9;")
init=init.replace("A.master.gain.value=outGain();","A.master.gain.value=.9;")
assert "outGain" not in init and "$(" not in init, "engine init still refers to the page"
i=init.index("  A.an=C.createAnalyser();");j=init.index("A.an.connect(C.destination);")+len("A.an.connect(C.destination);")
init=init[:i]+"  const _flt=host.makeFilter&&host.makeFilter();if(_flt){A.master.connect(_flt);_flt.connect(A.comp);A.flt=_flt}else A.master.connect(A.comp);A.comp.connect(A.lim);A.lim.connect(OUT);"+init[j:]
init=init.replace("setInterval(modTick,40);","").replace("  applyFx(cur(),C.currentTime);\n}","}")
assert 'setInterval' not in init and '$(' not in init and 'A.an' not in init, init[-600:]
# ---- runtime
run=run.replace("function modTick(){\n  const now=ctx.currentTime,ahead=.25,","function modTick(now){\n  const ahead=.25,")
run=run.replace("Math.random()","rand()")
assert 'function modTick(now)' in run and '$(' not in run
eng="""/* Worp engine for Ngoma: a copy of the sound engine of Worp (public/worp), pad only.
   Generated from public/worp/index.html by tools/sync_worp.py (deploy.sh runs it), so a seed sounds the same in both. Keep them in sync: rebuild, do not edit by hand.
   Runs in any AudioContext, live or offline; the host drives time with step(), so exports render the same way. */
(function(){
"""+gen+"""
function create(ctx,OUT,host){
  const A={};let CUR=null,rand=rng(1);
  const state={get key(){return host.key()},get deg(){return host.deg?host.deg():0},get res(){return host.res?host.res():4},get anchor(){return host.anchor||null},get cx(){return host.cx?host.cx():.3},cdv:0};
  const getBpm=()=>host.bpm();
  const cur=()=>CUR;
  const renderPatch=()=>{},renderFx=()=>{};
  let MOVE=.5,voicing=null,droneOn=false,lastT=-1,keyAt=-1,scAt='',bpmAt=0,barAt=-1,pendRel=false;
"""+init+run+"""
  function hostVoicing(P){
    const sc=SCALES.__host,n=sc.length,r=rng((((P._vs!=null?P._vs:P.seed))^0xBEEF)>>>0);   /* v171: the voicing comes from the pattern seed */let i5=sc.indexOf(7);if(i5<0)i5=Math.min(n-1,Math.round(n*.57));
    const v=[0,i5,n+r.pick([1,2,Math.min(3,n-1)])];if(r.chance(.6))v.push(r.pick([n+i5,2*n,2*n-1]));return v;
  }
  function startDrone(t){const o=(state.deg|0)+(state.cdv|0);voicing.forEach((d,i)=>polyOn('drone:'+i,state.key+36+semis(CUR.scale,d+o),.8,t));droneOn=true}
  function evolveDrone(t){
    const v=voicing,n=SCALES.__host.length;if(v.length<2)return;
    for(let k=0;k<8;k++){const i=1+Math.floor(rand()*(v.length-1)),d=v[i]+(rand()<.5?-1:1);
      if(d<1||d>2*n+2||v.includes(d))continue;v[i]=d;polyOn('drone:'+i,state.key+36+semis(CUR.scale,d+(state.deg|0)+(state.cdv|0)),.8,t);return}
  }
  function hostScale(){const iv=host.scale();SCALES.__host=iv.slice();return iv.join(',')}
  // Lead: one voice with glide playing the patch's phrase, one phrase step per host step, a small seeded change every four passes
  const KIND=host.kind==='lead'?'lead':'pad';
  function leadStop(t){[seqLead,seqLead2].forEach(c=>{if(c.voice){c.voice.release(t);c.voice=null}c.tied=false})}
  initGraph();
  return{
    get patch(){return CUR},
    setPatch(seed,t,mix,mute){
      if(CUR){for(const v of poly.values())v.release(t);poly.clear();retireFx(CUR);retireMods(CUR)}
      scAt=hostScale();keyAt=host.key()+'/'+(state.deg|0);bpmAt=getBpm();
      if(CUR)leadStop(t);
      const P=genPatch(seed>>>0,KIND);P.scale='__host';if(mix)P.mix=mix.slice(0,4);if(mute)P.mute=mute.slice(0,4);
      CUR=P;rand=rng((seed^0x2545F491)>>>0);if(KIND==='pad')voicing=hostVoicing(P);droneOn=false;applyFx(P,t);return P;
    },
    setMove(x,t){if(!CUR)return;MOVE=x;A.lfoGain.gain.setTargetAtTime(CUR.filter.lfoDepth*Math.min(2,x*2),t,.2);A.driftGain.gain.setTargetAtTime(CUR.drift*Math.min(2,x*2),t,.2)},   // Ngoma's Move: gate depth, or filter and pitch drift for pads without a gate
    noteOn(m,v,t){if(CUR)polyOn('key:'+m,m,v,t)},noteOff(m,t){polyOff('key:'+m,t)},   // Ngoma's MIDI keys
    setWet(r,e,t){if(e==null)e=r;[[A.wetR,r],[A.wetE,e],[A.fxE,e]].forEach(([n,x])=>{if(!ctx.currentTime)n.gain.value=x;else n.gain.setTargetAtTime(x,t,.05)})},
    setPhrase(seed){if(!CUR)return;const q=seed>>>0;if(CUR._ps===q)return;CUR._ps=q;const Q=genPatch(q,KIND);if(KIND==='lead'){CUR.phrase=Q.phrase;return}
      CUR._vs=q;CUR.change=Q.change;CUR.gate=Q.gate;rand=rng((q^0x2545F491)>>>0);if(droneOn){droneOn=false;pendRel=true}},   /* v171: a pad's pattern (voicing, how often it moves, gate) from a seed of its own; the sound stays */   // Ngoma's Lock: the line of one seed with the sound of another
    setMix(mix,mute,t){if(!CUR)return;CUR.mix=mix.slice(0,4);CUR.mute=mute.slice(0,4);applyMix(CUR,t)},
    step(g,t,BL,sw){
      if(!CUR)return;
      if(KIND==='lead'){
        if(g%BL===0){const sc=hostScale(),k=host.key()+'/'+(state.deg|0),b=getBpm();if(sc!==scAt||k!==keyAt){scAt=sc;keyAt=k}else if(b!==bpmAt){bpmAt=b;applyFx(CUR,t)}}
        state.cdv=host.cd?host.cd(g)|0:0;   /* v156: the line follows Ngoma's chords, one scale step per step of the chord root */
        {const R=host.rec,rs=host.res?host.res():4,spb=60/getBpm()/rs;if(R&&R.notes&&R.notes.length)playRec(R,g,t+(sw||0),spb,rs);else{PH_HOST=state;playPhrase(CUR,g,t+(sw||0),spb)}}modTick(t);return;
      }
      if(g%BL===0){
        const sc=hostScale(),k=host.key()+'/'+(state.deg|0),b=getBpm();
        if(sc!==scAt||k!==keyAt){scAt=sc;keyAt=k;for(const v of poly.values())v.release(t);poly.clear();retireFx(CUR);retireMods(CUR);voicing=hostVoicing(CUR);applyFx(CUR,t);droneOn=false}
        else if(b!==bpmAt){bpmAt=b;applyFx(CUR,t)}
      }
      if(pendRel){for(const v of poly.values())v.release(t);poly.clear();pendRel=false}
      {const R=host.rec;if(R&&R.notes&&R.notes.length){if(droneOn){for(const v of poly.values())v.release(t);poly.clear();droneOn=false}   /* v171: your recorded chords instead of the drone */
        const rs=host.res?host.res():4;playRec(R,g,t+(sw||0),60/getBpm()/rs,rs);lastT=t;gateStep(CUR,g*16/BL|0,t+(sw||0),MOVE*2);modTick(t);return}}
      {const cd=host.cd?host.cd(g)|0:0;if(cd!==(state.cdv|0)){const o0=(state.deg|0)+(state.cdv|0);state.cdv=cd;   /* v156: Ngoma's chords. Only the voices whose note changes move; common tones hold */
        if(droneOn)voicing.forEach((d,i)=>{const m0=state.key+36+semis(CUR.scale,d+o0),m=state.key+36+semis(CUR.scale,d+(state.deg|0)+cd);if(m!==m0)polyOn('drone:'+i,m,.8,t)})}}
      if(!droneOn||t-lastT>1.5){if(droneOn){for(const v of poly.values())v.release(t);poly.clear()}voicing=hostVoicing(CUR);startDrone(t);barAt=-1}
      lastT=t;
      if(g%BL===0){const bar=Math.floor(g/BL);if(barAt>=0&&bar!==barAt&&bar%CUR.change===0)evolveDrone(t);barAt=bar}
      gateStep(CUR,g*16/BL|0,t+(sw||0),MOVE*2);
      modTick(t);
    },
    stop(t){for(const v of poly.values())v.release(t);poly.clear();droneOn=false;leadStop(t)},
    setEnv(E){ENVA=E&&['a','d','s','r'].some(k=>E[k]!=null&&Math.abs(E[k]-.5)>.005)?{a:E.a,d:E.d,s:E.s,r:E.r}:null},
    setFilter(F,t){if(!A.flt)return;const p=A.flt.parameters,set=(k,v)=>{const q=p.get(k);if(q)q.setValueAtTime(v,t)},per=16*60/getBpm();
      set('cutoff',F.cut>=.999?20000:30*Math.pow(2,F.cut*9.38));set('res',F.res);set('drive',F.drive);set('model',F.model|0);set('env',F.env);set('lfo',F.lfo);
      set('per',per);const t0=host.t0?host.t0():0;set('t0',((t0%per)+per)%per)},
  };
}
window.WorpEngine={create,genPatch,genName,ENG,FX_NAME,PH_STYLES,phraseDesc,anchorFrom,phraseAt};
})();
"""
ng=os.path.join(HERE,'..','public','index.html')
s=open(ng).read()
import re
a=s.index('/* Worp engine for Ngoma');mz=re.compile(r'window\.WorpEngine=\{[^}]*\};\n\}\)\(\);\n').search(s,a);z=mz.end()
if s[a:z]==eng:
    print('Worp engine in Ngoma is up to date.')
else:
    open(ng,'w').write(s[:a]+eng+s[z:])
    print('Worp engine in Ngoma updated,',len(eng),'bytes.')
