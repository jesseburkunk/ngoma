/* Ngoma + Worp smoke test (v137). Plays every main function once in a headless browser and reports what broke.
   Run:  node tools/smoke.js            (needs Playwright; in the Claude workspace: PW=$(npm root -g)/playwright node tools/smoke.js)
   Optional: CHROME=/path/to/chromium. Exit code 1 when something fails. Takes about two minutes. */
const path = require('path'), http = require('http'), fs = require('fs');
let pw; try { pw = require(process.env.PW || 'playwright'); } catch (e) { console.log('Playwright not found. Install: npm i -D playwright && npx playwright install chromium'); process.exit(2); }
const ROOT = path.join(__dirname, '..', 'public');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.wasm': 'application/wasm' };
const srv = http.createServer((q, r) => { let f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html';
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); });

const results = []; let errs = [];
async function check(name, fn) { const t = Date.now(); let ok = true, note = '';
  /* A few checks lean on live audio timing and fail now and then by chance: a failed check runs once more before it counts (v147). */
  for (let attempt = 0; attempt < 2; attempt++) { const e0 = errs.length; ok = true; note = '';
    try { const r = await fn(); if (r === false) ok = false; else if (typeof r === 'string') note = r; } catch (e) { ok = false; note = String(e && e.message || e).split('\n')[0]; }
    const pe = errs.slice(e0); if (pe.length) { ok = false; note += (note ? ' | ' : '') + 'page error: ' + pe[0]; }
    if (ok) { if (attempt) note += (note ? ' | ' : '') + 'passed on the second try'; break; } }
  results.push({ name, ok, note }); console.log((ok ? 'PASS ' : 'FAIL ') + name + (note ? '  (' + note + ')' : '') + '  ' + ((Date.now() - t) / 1000).toFixed(1) + 's'); }
const assert = (c, m) => { if (!c) throw new Error(m); };

(async () => {
  await new Promise(r => srv.listen(0, r)); const base = 'http://localhost:' + srv.address().port + '/';
  const opts = { args: ['--autoplay-policy=no-user-gesture-required'] }; const exe = process.env.CHROME || (fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : null); if (exe) opts.executablePath = exe;
  const b = await pw.chromium.launch(opts); const ctx = await b.newContext(); const p = await ctx.newPage();
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  const hook = pg => { pg.on('pageerror', x => errs.push(x.message)); };
  hook(p); p.on('frameattached', () => {}); ctx.on('page', hook);
  const rmsJS = 'a=>{let s=0,bad=0;for(const v of a){if(!isFinite(v))bad++;s+=v*v}return bad?-1:Math.sqrt(s/a.length)}';

  await check('Ngoma loads', async () => { await p.goto(base + 'index.html'); await p.waitForTimeout(1500); await p.click('body', { position: { x: 5, y: 5 } });
    const ok = await p.evaluate(() => typeof S === 'object' && !!document.getElementById('leadStrip') && !!document.getElementById('scslots') && !!window.WorpEngine); assert(ok, 'UI or engine missing'); });

  await check('Every preset renders sound', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), bad = []; const bars = S.bars, lo = S.fx.leadOn, po = S.fx.padOn; S.bars = 1; S.fx.leadOn = false; S.fx.padOn = false;   /* drums only here: lead and pad have their own checks */
      for (const P of PRESETS) { applyPreset(P.id); S.fx.leadOn = false; S.fx.padOn = false; const w = await renderLoop(false, 22050), v = rms(w[0]); if (!(v > .002)) bad.push(P.id + ':' + (v < 0 ? 'NaN' : v.toFixed(4))); }
      S.bars = bars; S.fx.leadOn = lo; S.fx.padOn = po; return { n: PRESETS.length, bad }; }, rmsJS);
    assert(!r.bad.length, 'silent or broken: ' + r.bad.join(', ')); return r.n + ' presets'; });

  await check('Every pad type sounds', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), bad = []; S.bars = 1; S.fx.padOn = true; S.fx.padLvl = .5;
      for (const t of [...PAD_ORDER, 7]) { S.fx.padType = t; if (t === 7 && !S.fx.worp) S.fx.worp = { seed: 777, mix: [1, 1, 1, 1], mute: [false, false, false, false] };
        S.renderOnly = -1; const w = await renderLoop(false, 22050); S.renderOnly = null; const v = rms(w[0]); if (!(v > .0005)) bad.push(PAD_NAMES[t] + ':' + v.toFixed(5)); }
      S.fx.padOn = false; return bad; }, rmsJS); assert(!r.length, 'silent: ' + r.join(', ')); });

  await check('Lead sounds and sits in the mix', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), db = v => 20 * Math.log10(v + 1e-9), out = [];
      S.bars = 2; S.fx.leadOn = true; S.fx.leadLvl = .5;
      for (const sd of [4242, 12163, 20084]) { S.fx.wlead = { seed: sd, mix: [1, 1, 1, 1], mute: [false, false, false, false] };
        const m = await renderLoop(false, 22050); S.renderOnly = -2; const l = await renderLoop(false, 22050); S.renderOnly = null; out.push(+(db(rms(l[0])) - db(rms(m[0]))).toFixed(1)); }
      return out; }, rmsJS); assert(r.every(x => x > -16 && x < -3), 'lead vs mix dB ' + r.join(' ')); return 'lead ' + r.join(' / ') + ' dB under mix'; });

  await check('Every Magic mode renders', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), bad = []; S.bars = 1; S.fx.mgOn = true;
      for (let i = 0; i < MG_MODES.length; i++) { S.fx.mgMode = i; const w = await renderLoop(false, 22050), v = rms(w[0]); if (!(v > .002)) bad.push(MG_NAMES[i] + ':' + (v < 0 ? 'NaN' : v.toFixed(4))); }
      S.fx.mgOn = false; return { n: MG_MODES.length, bad }; }, rmsJS); assert(!r.bad.length, r.bad.join(', ')); return r.n + ' modes'; });

  await check('Export WAV (-16 LUFS, peaks under -1 dBTP)', async () => { const r = await p.evaluate(async () => { applyPreset(PRESETS[0].id); S.bars = 1; S.fx.leadOn = true; await dwPrepare();
      const buf = await (await fetch(DW.url)).arrayBuffer(), ac = new OfflineAudioContext(2, 1, 48000), a = await ac.decodeAudioData(buf), ch = [a.getChannelData(0), a.getChannelData(1)];
      return { sec: a.duration, lu: loudness(ch, a.sampleRate), tp: truePeak(ch) }; });
    assert(r.sec > .5, 'empty WAV'); assert(Math.abs(r.lu + 16) < 1.5 || r.tp > .85, 'loudness ' + r.lu.toFixed(1)); assert(r.tp <= Math.pow(10, -1 / 20) + .01, 'true peak ' + r.tp.toFixed(3));
    return r.sec.toFixed(2) + ' s, ' + r.lu.toFixed(1) + ' LUFS, peak ' + (20 * Math.log10(r.tp)).toFixed(1) + ' dBTP'; });

  await check('MIDI file export', async () => { const n = await p.evaluate(() => midiBytes(S.bars * 4 * S.res).length); assert(n > 40, 'MIDI too small: ' + n); });

  await check('Live play makes sound', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj); S.lanes.forEach(L => L.mute = false); start(); await new Promise(r => setTimeout(r, 1000)); let v = 0;
      for (let k = 0; k < 10; k++) { await new Promise(r => setTimeout(r, 80)); const a = new Float32Array(2048); AG.scopeTap.aL.getFloatTimeDomainData(a); v = Math.max(v, rms(a)); } return { v, playing }; }, rmsJS); assert(r.playing && r.v > .005, 'live rms ' + r.v); });

  await check('Drums off silences every drum, M toggles it', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), w = ms => new Promise(r => setTimeout(r, ms)), lvl = () => { const a = new Float32Array(2048); AG.scopeTap.aL.getFloatTimeDomainData(a); return rms(a); };
      const lo = S.fx.leadOn, po = S.fx.padOn; S.fx.leadOn = false; S.fx.padOn = false; syncGraph(AG); leadSync(AG); padSync(AG); await w(600); const on = lvl();
      document.getElementById('drumsoff').click(); await w(2500); let off = 0; for (let k = 0; k < 6; k++) { await w(100); off = Math.max(off, lvl()); }   /* reverb and echo tails may still ring out */ 
      const dbg = { pad: AG.pad.out && AG.pad.out.gain.value, lead: AG.lead.out.gain.value, mg: S.fx.mgOn, dl: AG.dlAll.gain.value, lanesG: AG.lanes.map(l => +l.dg.gain.value.toFixed(2)).join(''), wlead: !!AG.wlead, worp: !!AG.worp };
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'm' })); let back = 0; for (let k = 0; k < 10; k++) { await w(100); back = Math.max(back, lvl()); } S.fx.leadOn = lo; S.fx.padOn = po; syncGraph(AG); return { on, off, back, state: drumsOff, dbg }; }, rmsJS);
    assert(r.on > .01 && r.off < Math.max(.003, r.on * .25) && r.back > .01 && !r.state, JSON.stringify(r)); });

  await check('Keyboard shortcuts do not throw', async () => { for (const k of ['t', 'm', 'm', 'ArrowLeft', 'ArrowRight']) { await p.keyboard.press(k); await p.waitForTimeout(80); } await p.keyboard.down('d'); await p.waitForTimeout(150); await p.keyboard.up('d'); });

  await check('Undo and redo', async () => { const r = await p.evaluate(() => { const L = S.lanes[0], before = L.level; hRecord(() => { L.level = before * .5; }); updHist(); const mid = S.lanes[0].level; hStep(-1); const back = S.lanes[0].level; hStep(1); return [before, mid, back, S.lanes[0].level]; });
    assert(r[1] === r[0] * .5 && r[2] === r[0] && r[3] === r[0] * .5, 'level ' + r.join(' ')); await p.evaluate(() => hStep(-1)); });

  await check('Scenes and Morph', async () => { const r = await p.evaluate(async () => { const w = ms => new Promise(r => setTimeout(r, ms)), sig = () => S.lanes.map(L => L.steps.filter(Boolean).length).join(',');
      S.scenes = S.scenes.map(() => null); S.morph = 2; sceneStore(0); const A = sig();
      S.lanes.forEach(L => { L.steps = L.steps.map(() => null); }); S.lanes[6].steps = S.lanes[6].steps.map((v, j) => j % 2 ? { v: .8 } : null); sceneStore(1); const B = sig();
      sceneRecall(0); const seen = new Set(); let t = 0, started = false;
      while (t < 12000) { await w(250); t += 250; if (MORPH.on) { started = true; seen.add(sig()); } else if (started) break; }
      return { A, B, end: sig(), started, mids: [...seen].filter(s => s !== A && s !== B).length }; });
    assert(r.started, 'morph never started'); assert(r.end === r.A, 'did not land on the scene'); assert(r.mids >= 2, 'no gradual steps (' + r.mids + ')'); return r.mids + ' in-between states'; });

  await check('Worp panel: keys play Ngoma lead, record a line on the grid, Mine | Worp', async () => {
    await p.evaluate(() => { S.fx.leadOn = true; if (!playing) start(); worpPanel(true, worpToken(leadSpec(), 'lead')); }); await p.waitForTimeout(2500);
    const f = p.frames().find(x => x.url().includes('/worp')); assert(f, 'no Worp frame'); f.page();
    const r1 = await f.evaluate(async () => { initAudio(); onMidi({ data: [0x90, 67, 110] }); const routed = KEYS_NG.size; await new Promise(r => setTimeout(r, 200)); onMidi({ data: [0x80, 67, 0] }); return { routed, kind: cur().kind }; });
    assert(r1.kind === 'lead' && r1.routed === 1, 'keys not routed to Ngoma');
    await f.evaluate(() => recLine()); const wait = await f.evaluate(() => REC.start - ctx.currentTime); await p.waitForTimeout(wait * 1000 + 300);
    await f.evaluate(async () => { const w = ms => new Promise(r => setTimeout(r, ms)); await w(90); onMidi({ data: [0x90, 64, 100] }); await w(250); onMidi({ data: [0x80, 64, 0] }); await w(330); onMidi({ data: [0x90, 67, 90] }); await w(120); onMidi({ data: [0x80, 67, 0] }); });
    const endIn = await f.evaluate(() => REC.end - ctx.currentTime); await p.waitForTimeout(endIn * 1000 + 1200);
    const r2 = await p.evaluate(() => { const R = leadSpec().rec, sg = document.getElementById('leadLine'), mine = sg.querySelector('[data-l=mine]'), wo = sg.querySelector('[data-l=worp]');
      const a = { n: R && R.notes.length, shown: !sg.hidden && !mine.disabled, grid: R && R.notes.every(x => Math.abs(x.s - Math.round(x.s)) < 1e-6 && Math.abs(x.d - Math.round(x.d)) < 1e-6) };
      wo.click(); a.off = !recOn(); mine.click(); a.on = !!recOn(); a.lrec = LREC; return a; });
    assert(r2.n >= 1, 'line not recorded'); assert(r2.grid, 'recording not on the grid at Quantize 100%'); assert(r2.shown && r2.off && r2.on, 'Mine | Worp switch'); assert(!r2.lrec, 'lead left muted after recording');
    const r3 = await f.evaluate(async () => { const sg = document.getElementById('lineSeg'), mine = sg.querySelector('[data-l=mine]'), wo = sg.querySelector('[data-l=worp]'); const vis = !sg.hidden && !mine.disabled;
      wo.click(); await new Promise(r => setTimeout(r, 700)); const off = !state.rec && !mine.disabled; mine.click(); await new Promise(r => setTimeout(r, 700)); return { vis, off, on: !!state.rec, ring: !!ringAn() }; });
    const r4 = await p.evaluate(() => { const a = { ng: !!recOn() }; worpPanel(false); return a; });
    assert(r3.vis && r3.off && r3.on && r4.ng, 'Mine | Worp in Worp ' + JSON.stringify([r3, r4])); assert(r3.ring, 'Worp ring has no signal source over Ngoma');
    await p.evaluate(() => { const W = leadSpec(); delete W.rec; save(); }); });

  await check('Vet: renders, on and off at about the same loudness, peaks held', async () => { const r = await p.evaluate(async () => { applyPreset(PRESETS[0].id); S.bars = 1; const lo = S.fx.leadOn; S.fx.leadOn = false; const o = [];
      for (const [on, a] of [[false, .3], [true, .3], [true, 1]]) { S.fx.vetOn = on; S.fx.vetAmt = a; const w = await renderLoop(false, 22050), ch = [w[0], w[1] || w[0]]; let pk = 0; for (const c of ch) for (const v of c) pk = Math.max(pk, Math.abs(v)); o.push({ lu: loudness(ch, 22050), pk }); }
      S.fx.vetOn = true; S.fx.vetAmt = FX_DEFAULT.vetAmt; S.fx.leadOn = lo; syncGraph(AG); return o; });
    assert(r.every(x => isFinite(x.lu) && x.lu > -40), 'silent or NaN ' + JSON.stringify(r)); assert(Math.abs(r[1].lu - r[0].lu) < 1.5 && Math.abs(r[2].lu - r[0].lu) < 2.5, 'loudness jump ' + r.map(x => x.lu.toFixed(1)).join(' '));
    assert(r.every(x => x.pk < 1), 'sample peak over 0 dBFS ' + r.map(x => x.pk.toFixed(3)).join(' ')); return r.map(x => x.lu.toFixed(1)).join(' / ') + ' LUFS (off / 30% / 100%)'; });

  await check('MIDI control: target, Tight lands on the grid', async () => { const r = await p.evaluate(() => { if (!playing) start(); const o = {}; S.fx.leadOn = true; S.fx.padOn = true; S.fx.padType = 7;
      S.midiTo = 'pad'; o.pad = midiDest(); S.midiTo = 'lead'; o.lead = midiDest(); S.fx.leadOn = false; o.fall = midiDest(); S.fx.leadOn = true; midiUI(); o.btn = document.getElementById('midibtn').textContent;
      S.midiQ = true; const sd = stepDur(S), now = actx.currentTime, t = midiQT(now); let g = gStep - 64, best = 9; for (; g < gStep + 8; g++) best = Math.min(best, Math.abs(nextT + (g - gStep) * sd + grooveOff(g, S, sd) - t));
      o.onGrid = t === now || best < 1e-6; o.ahead = t - now; S.midiQ = false; o.free = midiQT(now) === now; return o; });
    assert(r.pad === 'pad' && r.lead === 'lead' && r.fall === 'pad', 'target ' + JSON.stringify(r)); assert(r.onGrid && r.ahead >= 0 && r.ahead <= .5 && r.free, 'Tight ' + JSON.stringify(r)); return r.btn; });

  await check('Clear a track, undo brings it back; lanes grouped low, mid, high', async () => { const r = await p.evaluate(() => { S.compact = true; renderLanes(); const b = document.querySelector('.lane .tg.clr'), i = +b.closest('.lane').dataset.i;
      b.click(); const o = { gone: !hasHits(S.lanes[i]), vis: !!document.querySelector('.lane[data-i="' + i + '"]') }; hStep(-1); o.back = hasHits(S.lanes[i]); renderLanes();
      const regs = [...document.querySelectorAll('.lane')].map(e => INSTR[+e.dataset.i].reg), R = { low: 0, mid: 1, high: 2 }; o.sorted = regs.every((g, k) => !k || R[regs[k - 1]] <= R[g]); return o; });
    assert(r.gone && r.vis && r.back && r.sorted, JSON.stringify(r)); });

  await check('Fresh and New buttons', async () => { await p.evaluate(() => { ['fresh', 'leadNew', 'padNew', 'worpNew'].forEach(id => { const e = document.getElementById(id); if (e) e.click(); }); }); await p.waitForTimeout(500); });

  await check('MIDI keys play the lead before Play and after closing Worp', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), w = ms => new Promise(r => setTimeout(r, ms));
      stop(); await w(300); S.fx.leadOn = true; S.fx.padOn = false; const peak = async () => { let v = 0; ngMidi({ data: [0x90, 64, 110] }); for (let k = 0; k < 5; k++) { await w(40); const a = new Float32Array(2048); AG.scopeTap.aL.getFloatTimeDomainData(a); v = Math.max(v, rms(a)); } ngMidi({ data: [0x80, 64, 0] }); await w(300); return v; };
      const a = await peak(); worpPanel(true, worpToken(leadSpec(), 'lead')); await w(1500); worpPanel(false); await w(200); const b = await peak(); return { a, b }; }, rmsJS);
    assert(r.a > .01 && r.b > .01, JSON.stringify(r)); });

  await check('Old shared links still open', async () => { const link = await p.evaluate(async () => { const str = JSON.stringify({ pattern: patternData(), kit: kitData() });
      const cs = new CompressionStream('deflate-raw'), wr = cs.writable.getWriter(); wr.write(new TextEncoder().encode(str)); wr.close(); const u = new Uint8Array(await new Response(cs.readable).arrayBuffer());
      let b = ''; u.forEach(x => b += String.fromCharCode(x)); return location.href.split('#')[0] + '#s=' + btoa(b).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); });
    await p.goto('about:blank'); await p.goto(link); await p.waitForTimeout(1800); const st = await p.evaluate(() => document.getElementById('status').textContent); assert(/shared pattern/.test(st), 'status: ' + st); });

  await check('Saved state survives a reload', async () => { const a = await p.evaluate(async () => { stop(); S.bpm = 97; save(); await new Promise(r => setTimeout(r, 1300)); return { bpm: S.bpm, pre: S.preset, sig: S.lanes.map(L => L.steps.filter(Boolean).length).join() }; });
    await p.reload(); await p.waitForTimeout(1500); const c = await p.evaluate(() => ({ bpm: S.bpm, pre: S.preset, sig: S.lanes.map(L => L.steps.filter(Boolean).length).join() }));
    assert(JSON.stringify(a) === JSON.stringify(c), JSON.stringify(a) + ' vs ' + JSON.stringify(c)); });

  /* v150: checks for what came in v143 to v149 */
  await check('Every, Life and Ghosts: seeded, ghost lines only with Life', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj);
      applyPreset('qawstep'); S.life = .35; const sig = () => { const o = []; for (let g = 0; g < 64; g++) for (const e of eventsAt(g, S)) o.push(g + ':' + e.lane + ':' + e.v.toFixed(4) + (e.life ? 'L' : '')); return o.join(','); };
      const a = sig(), b = sig(), ghosts = (a.match(/L/g) || []).length; S.life = 0; const z = sig(), g0 = (z.match(/L/g) || []).length; S.life = .35;
      S.bars = 1; S.fx.mgOn = true; S.fx.mgMode = MG_NAMES.indexOf('Ghosts'); S.fx.mgEvery = 4; S.fx.mgChance = 1; const w = await renderLoop(false, 22050), v = rms(w[0]); S.fx.mgOn = false; S.fx.mgEvery = 1;
      return { same: a === b, ghosts, g0, v, every: evN('rvEvery') }; }, rmsJS);
    assert(r.same, 'Life is not seeded'); assert(r.ghosts > 0 && r.g0 === 0, 'ghost line ' + r.ghosts + '/' + r.g0); assert(r.v > .002, 'Ghosts silent'); assert(r.every === 1, 'Every default'); return r.ghosts + ' ghost strokes in 4 bars'; });

  await check('Master: bass in mono, the rest keeps its place', async () => { const r = await p.evaluate(async () => { const out = [];
      for (const f of [60, 2000]) { const oc = new OfflineAudioContext(2, 22050, 44100), V = buildVet(oc), o = oc.createOscillator(), pn = oc.createStereoPanner(); o.frequency.value = f; pn.pan.value = .5; o.connect(pn).connect(V.in); V.out.connect(oc.destination);
        V.dry.gain.value = 0; V.wet.gain.value = 1; V.sh.curve = masterCurve(0); o.start(); const bu = await oc.startRendering(), L = bu.getChannelData(0), R = bu.getChannelData(1); let l = 0, rr = 0; for (let i = 11025; i < 22050; i++) { l += L[i] * L[i]; rr += R[i] * R[i]; } out.push(10 * Math.log10(rr / l)); }
      return out; });
    assert(Math.abs(r[0]) < 1.2, 'low end not mono: ' + r[0].toFixed(2) + ' dB'); assert(Math.abs(r[1] - 7.65) < 1, 'panning changed: ' + r[1].toFixed(2) + ' dB'); return '60 Hz ' + r[0].toFixed(1) + ' dB, 2 kHz ' + r[1].toFixed(1) + ' dB'; });

  await check('Morph: an edit finishes it first, a knob you turn stays', async () => { const r = await p.evaluate(async () => { const w = ms => new Promise(r => setTimeout(r, ms));
      stop(); await w(200); applyPreset(PRESETS.find(x => x.trad === 'cuba').id); S.bpm = 170; S.morph = 2; afterLoad(); sceneStore(0); applyPreset(PRESETS.find(x => x.trad === 'me').id);   /* v165: by tradition, not by index (new rhythms shift the list) */ S.bpm = 170; afterLoad(); sceneStore(1);
      start(); await w(200); sceneRecall(0); let t = 0; while (!MORPH.on && t < 40) { await w(100); t++; } const on = MORPH.on, banner = !document.getElementById('morphInd').hidden;
      await w(600); S.fx.eqLow = 5; await w(900); const kept = S.fx.eqLow; editCell(0, 1, 'cycle'); const after = MORPH.on, hid = document.getElementById('morphInd').hidden; stop(); S.fx.eqLow = 0; syncGraph(AG);
      return { on, banner, kept, after, hid, low: S.fx.eqLow }; });
    assert(r.on && r.banner, 'no morph or banner ' + JSON.stringify(r)); assert(r.kept === 5, 'knob overwritten ' + JSON.stringify(r)); assert(!r.after && r.hid, 'edit did not finish the morph ' + JSON.stringify(r)); });

  await check('Max for Live bridge: Live starts Ngoma, sets the tempo and keeps time', async () => { const m = await ctx.newPage();
    await m.addInitScript(() => { window.__H = {}; window.__out = []; window.max = { bindInlet: (n, f) => { window.__H[n] = f; }, outlet: (...a) => window.__out.push(a) }; });
    await m.goto(base + 'index.html'); await m.waitForTimeout(1500); await m.click('body', { position: { x: 5, y: 5 } });
    const r = await m.evaluate(async () => { const w = ms => new Promise(r => setTimeout(r, ms)), bpm = 124; ensureCtx(); await w(300); const sr = actx.sampleRate, spb = 60 / bpm * sr; let beats = 0; const c0 = actx.currentTime;   /* Live at the page's rate, so the context is not rebuilt mid-test */   /* Live's beat clock runs on the same audio clock */
      for (let k = 0; k < 40; k++) { beats = 1 + (actx.currentTime - c0) * bpm / 60; window.__H.live(1, beats, spb, sr); await w(50); }
      const o = { on: M4L.on, playing, bpm: S.bpm, ready: window.__out.length > 0, lag: ((beats = 1 + (actx.currentTime - c0) * bpm / 60) + (M4L.lat + M4L.off) * bpm / 60) - (gStep - (nextT - actx.currentTime) / (60 / S.bpm / S.res)) / S.res };
      window.__H.live(0, beats, spb, sr); await w(100); o.stopped = !playing; return o; });
    await m.close(); assert(r.on && r.ready && r.playing, 'bridge not up ' + JSON.stringify(r)); assert(Math.abs(r.bpm - 124) < .01, 'tempo ' + r.bpm); assert(r.stopped, 'did not stop');
    assert(Math.abs(r.lag) < .02, 'out of step with Live by ' + r.lag.toFixed(3) + ' beats'); return 'lag ' + r.lag.toFixed(3) + ' beat'; });

  await check('Chords: Drone changes nothing, a scheme moves the pad and the tuned drums', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj);
      const keep = JSON.stringify(S.fx); S.bars = 4; S.fx.padOn = true; S.fx.padLvl = .5; S.fx.padType = 0; S.fx.chBars = 1; S.renderOnly = -1;
      S.fx.chProg = 'drone'; const d0 = [0, 16, 32, 48].map(g => chordAt(g)); const a = await renderLoop(false, 22050);
      S.fx.chProg = 'montuno'; const d1 = [0, 16, 32, 48].map(g => chordAt(g)), names = d1.map(chName); const b = await renderLoop(false, 22050);
      const si = INSTR.findIndex(x => x.id === 'surdo'), L0 = S.lanes[si], t0 = L0.tune; { const r0 = ((INSTR[si].base + (S.fx.kitPitch || 0) - S.key) % 12 + 12) % 12; L0.tune = r0 > 6 ? 12 - r0 : -r0; }   /* the surdo on the root */
      const sm = INSTR[si].base + L0.tune + (S.fx.kitPitch || 0), sc = SCALES[S.scale].iv;
      const drum = [0, 16, 32, 48].map(g => { const d = chordAt(g), pc = (((sm + chTn(si, g) - S.key) % 12) + 12) % 12; return { ok: pc === (sc[((d % sc.length) + sc.length) % sc.length] + ((sm - S.key) % 12 + 12) % 12 - sc[0]) % 12 || d === 0, mv: chTn(si, g) }; });
      const shk = chTn(INSTR.findIndex(x => x.id === 'shaker'), 16); S.fx.chDrums = false; const off = chTn(si, 16); S.fx.chDrums = true; L0.tune = t0; S.fx.chProg = 'montuno'; const cm = chordMidiBytes(64).length, cl = chLen();
      S.fx.chProg = 'wander'; const w1 = [0, 1, 2, 3, 4, 5].map(k => chordAt(k * 16)), w2 = [0, 1, 2, 3, 4, 5].map(k => chordAt(k * 16));
      let diff = 0; for (let i = 0; i < a[0].length; i += 7) diff += Math.abs(a[0][i] - b[0][i]);
      S.renderOnly = null; Object.assign(S.fx, JSON.parse(keep)); return { d0, d1, names, ra: rms(a[0]), rb: rms(b[0]), diff, w: w1.join() === w2.join() && new Set(w1).size > 1, drum, shk, off, cm, cl }; }, rmsJS);
    assert(r.cm > 60 && r.cl === 64, 'chord MIDI ' + r.cm + ' bytes, scheme ' + r.cl + ' steps');
    assert(r.drum.every(x => x.ok) && r.drum.some(x => x.mv), 'surdo does not follow the root ' + JSON.stringify(r.drum)); assert(r.shk === 0 && r.off === 0, 'shaker moved or Drums too ignored');
    assert(r.d0.every(x => x === 0), 'drone moved ' + r.d0); assert(new Set(r.d1).size >= 3, 'scheme flat ' + r.d1); assert(r.ra > .0005 && r.rb > .0005, 'silent');
    assert(r.diff > 1, 'the pad did not follow'); assert(r.w, 'wander not seeded'); return r.names.join(' ') + ', surdo ' + r.drum.map(x => x.mv).join('/') + ' st, wander seeded'; });

  await check('Voice cache: live hits play from buffers that sound like the synthesis', async () => { const r = await p.evaluate(async () => {
      const i = INSTR.findIndex(x => x.id === 'conga'), sp = vcSpec(i, 0, 0, 1, true, [.1, .2, .3], 0, 1); if (!sp) return { err: 'no spec' };
      ensureCtx(); const sr = actx.sampleRate; vcGet(sp, sr); for (let k = 0; k < 60 && !VC.map.get(sp.key); k++) await new Promise(r => setTimeout(r, 50));
      const buf = VC.map.get(sp.key); if (!buf) return { err: 'not rendered' }; const oc = new OfflineAudioContext(1, Math.ceil(sr * 1.2), sr);
      voiceKind(oc, oc.destination, INSTR[i], 0, 0, sp.vl, true, [VCR[sp.k][0], Math.max(-1, Math.min(1, VCR[sp.k][1] + sp.e)), VCR[sp.k][2]], sp.m, mtof(sp.m), sp.T, sp.tv); const ref = await oc.startRendering();
      const rms = a => { let s = 0; for (const v of a) s += v * v; return Math.sqrt(s / a.length); }, n = Math.min(buf.length, ref.length), A = buf.getChannelData(0).subarray(0, n), B = ref.getChannelData(0).subarray(0, n);
      const db = 20 * Math.log10(rms(A) / rms(B)); start(); await new Promise(r => setTimeout(r, 4000)); const o = { db, hit: VC.hit, miss: VC.miss, size: VC.map.size }; stop(); return o; });
    assert(!r.err, r.err); assert(Math.abs(r.db) < 1.5, 'cached hit differs ' + r.db.toFixed(2) + ' dB'); assert(r.hit > 0, 'no hits from the cache (' + r.miss + ' misses)');
    return r.hit + ' hits from ' + r.size + ' buffers, ' + r.miss + ' synthesised while filling'; });

  await check('Load budget: layers do not cost more than they should', async () => { const r = await p.evaluate(async () => { const keep = JSON.stringify(S.fx), b0 = S.bars; S.bars = 2;
      const t = async fn => { Object.assign(S.fx, JSON.parse(keep)); fn && fn(); let best = 1e9; for (let k = 0; k < 2; k++) { const t0 = performance.now(); await renderLoop(false, 48000); best = Math.min(best, performance.now() - t0); } return best; };
      const d = await t(), all = await t(() => { S.fx.padOn = true; S.fx.padType = 7; S.fx.leadOn = true; S.fx.mgOn = true; S.fx.mgMode = 1; S.fx.rvType = 'bloom'; S.fx.rvLevel = .3; });
      Object.assign(S.fx, JSON.parse(keep)); S.bars = b0; return { d, all, x: all / d, rt: d / 1000 / (2 * 4 * 60 / S.bpm) }; });
    assert(r.x < 3.3, 'everything on costs ' + r.x.toFixed(2) + ' x the drums alone (budget 3.3)'); return 'all on ' + r.x.toFixed(2) + ' x drums, drums ' + r.rt.toFixed(2) + ' x real time here'; });

  await check('Bloom: renders, the tail sings and stays in bounds', async () => { const r = await p.evaluate(async rj => { const rms = eval(rj), keep = JSON.stringify(S.fx); S.bars = 2;
      Object.assign(S.fx, { rvOn: true, rvType: 'hall', rvLevel: .5 }); const a = await renderLoop(false, 22050); S.fx.rvType = 'bloom'; const b = await renderLoop(false, 22050);
      let pk = 0; for (const v of b[0]) pk = Math.max(pk, Math.abs(v)); const hz = bloomHz(0); Object.assign(S.fx, JSON.parse(keep)); return { ra: rms(a[0]), rb: rms(b[0]), pk, hz }; }, rmsJS);
    assert(r.rb > 0 && r.ra > 0, 'silent or not finite'); assert(r.pk <= 2, 'runaway feedback, peak ' + r.pk);   /* the folded-back tail may sum a little over 1 before the export normalises; a runaway loop would be far higher */ assert(r.hz.every(f => f >= 330 && f <= 1400), 'bank ' + r.hz);
    return 'bank ' + r.hz.map(Math.round).join('/') + ' Hz'; });

  await p.close();   /* else Worp links to this Ngoma tab and plays there */
  const w = await ctx.newPage();
  await check('Worp alone: loads, rolls, pads and leads sound', async () => { await w.goto(base + 'worp/index.html'); await w.waitForTimeout(1500); await w.click('body', { position: { x: 5, y: 5 } });
    const r = await w.evaluate(async rj => { const rms = eval(rj), wt = ms => new Promise(r => setTimeout(r, ms)); initAudio(); const got = { pad: 0, lead: 0 }, bad = [];
      for (const mode of ['pad', 'pad', 'pad', 'lead', 'lead', 'lead']) { state.mode = mode; roll(); startPlay(); let v = 0;
        for (let k = 0; k < 12; k++) { await wt(250); const a = new Float32Array(2048); A.an.getFloatTimeDomainData(a); v = Math.max(v, rms(a)); }
        stopPlay(); await wt(200); if (v > .002) got[cur().kind]++; else bad.push(mode + ':' + cur().name + ':' + v.toFixed(4)); }
      return { got, bad }; }, rmsJS);
    assert(r.got.pad === 3 && r.got.lead === 3, JSON.stringify(r)); return 'pads ' + r.got.pad + ', leads ' + r.got.lead; });

  await b.close(); srv.close();
  const f = results.filter(r => !r.ok); console.log('\n' + (results.length - f.length) + '/' + results.length + ' passed' + (f.length ? '. Failed: ' + f.map(r => r.name).join('; ') : '.'));
  process.exit(f.length ? 1 : 0);
})().catch(e => { console.log('Smoke test crashed: ' + e.message); process.exit(1); });
