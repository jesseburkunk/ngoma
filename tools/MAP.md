# Ngoma + Worp: code map

Start here every round. The handwritten part (this top half) says how things hang together; the index below the marker lists
every section and top-level function with its line number. Refresh the index after each round: `python3 tools/map.py`.
Find anything else with `grep -n "function name" public/index.html`. Lines are long: cut with `cut -c1-400`.

## Files
- `public/index.html`: Ngoma, one file. Order: CSS (2 style blocks; new rules in the second), HTML, script 1 = Worp engine
  (generated, do not edit), script 2 = Ngoma: ENGINE (pure pattern logic) > STATE > AUDIO > UI > EXPORT and the rest.
- `public/worp/index.html`: Worp, one file. The engine sections (seeded dice up to voices, minus the master filter) are copied
  into Ngoma by `tools/sync_worp.py`. Change the engine here, then run the sync. Engine API extras (setFilter, setEnv) live in sync_worp.py.
- `tools/check.js` compiles every script; `tools/smoke.js` 21 browser checks (Playwright; run in the cloud container, see overdracht).
- `backup/`: a copy of each file before a round. `README.md`: one line per version, Ngoma and Worp.

## Signal flow in Ngoma (buildGraph, AUDIO)
Drum voice() > lane.in > shaper sh > dg (drop / drums off) > g (level) > p (pan) > master
- per lane, from g: rG > rs (track reverb send L.rev) > reverb; eG > ds (track delay send L.dly) > delay; eG > dlHp > dlAll (kit delay send dlSend) > delay
- per lane, p > duck (gain 1, hook) > master; p > Ghosts loop (gIn > gD with gFb > gHp > gBp/gCl > gLp > gPan > gOut > master and reverb), glitchStep
- per lane, from p: mG > Magic inputs (mIn for Resonate, Comb, Air, Formant; cIn for Cosmos). rG/eG/mG are the Every gates (hitGate, v143)
- g > sc > scBus: sidechain for the filter Env
duck > Room (buildRoom, early reflections, roomSync) > master. master > sub hp > EQ (eqL, eqM, eqH) > eqC / AudioWorklet filter (ngoma-filter) > Master (buildVet/vetSync, keys vetOn/vetAmt: glue comp, tape, M/S with LR4 bass mono + allpass on mid, side shelf, air, VET_TRIM) > bus comp > limiter > 4x soft clip > ceiling > vol > out
Magic outputs (Resonate, Comb, Air, Formant, Glitch) also feed eBus > Magic's own dub echo (buildDub, synced in magicSync). Reverb, delay, Magic, pad (buildPad) and lead (buildLead) all return into master. Worp pad and lead: G.worp / G.wlead engines, their filter via host.makeFilter.

## Time and state
- Life (v147): S.life; lifeInfo(S) picks prominent lanes (prom, drift) and the ghost-line lane (poly); used in eventsAt (velocity swell, 3-against-4 ghosts with e.life) and driftAt.
- `S` is the whole state; `S.fx` all sound settings (defaults FX_DEFAULT, migrations right after it). `save()` is debounced (~1.3 s).
- `scheduleStep(ctx,G,g,t)` runs per sixteenth, live and offline: pad/lead bars, Magic steps, then every drum event (eventsAt).
  Offline export uses the same graph and scheduler (renderLoop), so whatever is seeded by g stays identical in the export.
- UI refresh: functions pushed into `UPD` run after a state change. Knobs: makeKnob / makeSegK / makeSelK. Range sliders: frng. Selects: fsel.
- Audio sync after a change: fxSync(heavy) > syncGraph(G) > syncFx(G); Magic: magicSync(G); pad: padSync; lead: leadSync.
- Morph: MORPH state, morphStart/morphSet/morphEnd; user-touched settings in MORPH.user/ul are left alone; morphSnap() finishes a morph before an edit; morphInd() banner; scBase/scEdited for the edited dot.
- Undo: hRecord(fn) around a change. Scenes and morph snapshot S.fx: new keys must survive being undefined.

## Ngoma and Worp talking
Same origin: BroadcastChannel plus postMessage for the embedded Worp panel (worpPanel). Messages from Worp: hello, key, play, stop,
audition, edit, use, close, line, lineoff, linerec, recdata. A sound travels as a token:
`worp-{pad|lead}-{seed36}-{mutes}-{mix}-f{filter}[-e{adsr}]` (shareToken/parseToken in Worp, worpToken/worpParse in Ngoma).
Ngoma keeps it in S.fx.worp (pad) and S.fx.wlead (lead) with .mix .mute .flt .env.

## Where to change typical things
- A new drum-bus effect or send: buildGraph lanes + buildMagic / buildReverb / buildDelay, settings in syncFx, UI in the Sound section.
- A Magic mode: MG_MODES (index = saved mgMode, only append), buildMagic, procSync, a step function called from scheduleStep (combStep, formantStep, resStep, glitchStep). Magic knobs: the block with makeSelK({label:'Mode'...; contextual knobs hide via .hidden in kw.upd.
- Resonate notes: resChord(g) (MG_CHORDS), sent by resMsg.
- A Worp sound parameter: genPatch (Worp), Voice / ampOf, then token + Ngoma worpParse, then sync_worp.py.
- Layers (pad/lead units in Ngoma): unitFlt / unitWet / unitEcho / unitTr, knobs in the lead and pad UI blocks (search 'leadSlot').
- Help texts: the <dl> in the Help dialog (search '<dt>Magic</dt>').

## Round checklist
backup > build (python read-modify-write on the Mac, assert each replace matches once) > sync_worp.py > check.js > smoke once at the end
> README line > `python3 tools/map.py` > update claude/ngoma-overdracht.md.

<!-- AUTO: below this line tools/map.py writes; do not edit by hand -->

## Ngoma: public/index.html (5193 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 429): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 454): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 472): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 482): (no functions)
- **Scenes (v91)** (line 494): (no functions)
- **Changes on the next bar (v88)** (line 520): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 530): (no functions)
- **script starts** (line 1249): mtof 1264, mod 1265
- **seeded dice** (line 1267): rng 1268, scaleLabel 1279, semis 1280
- **patch generation: chance inside musical limits** (line 1282): genSpectrum 1283, fromHist 1297, histEntry 1298, genName 1299, uniqueName 1308, genPatch 1309
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1417): anchorFrom 1435, euclidW 1437, genPhraseStyle 1438, rnd01 1477, phraseAt 1480, phraseAt0 1482, phCx 1490, phZ 1491, phraseCore 1492, phraseDesc 1527
- **the modular part: sources, cables, re-patching** (line 1529): genMods 1532, genFx 1584, fxDesc 1612, destRange 1621, destName 1633, srcDesc 1634, create 1644, makeIR 1651, curve 1664, initGraph 1665, gateStep 1696, prepWaves 1698, applyFx 1705, mixVal 1727, applyMix 1728, loopD 1730, airNorm 1731, foldCurve 1732, bitCurve 1735, quantCurve 1736, chroma 1737, fxRotor 1744, fxBitplane 1752, fxHalo 1759, fxStrings 1777, fxShifter 1785, fxSonar 1799, buildFx 1809, retireFx 1817, globalParams 1821, buildMods 1822, retireMods 1843, modTick 1849, envMul 1885, ampOf 1886, Voice 1889
- **voices** (line 2004): polyOn 2006, polyOff 2011, mono 2012, playRec 2018, playPhrase 2022, releaseAll 2025
- **script starts** (line 2087): (no functions)
- **ENGINE** (line 2113): isMan 2139, kickOn 2140, kickHeld 2141, rnd 2302, euclid 2307, charOf 2312, genSteps 2313, varWeight 2340, mutateSteps 2341, mutateStepsX 2342, variant 2376, anySolo 2381, fillOn 2383, condOk 2385, dlgPalette 2400, dlgPlan 2402, lifeInfo 2426, eventsAt 2433, stepDur 2464, grooveOff 2468, hitsOf 2478, midiNote 2483, mname 2491, inScale 2492, snap 2493, nearestPC 2494
- **STATE** (line 2497): panMig 2503, freshLane 2507, lanesFrom 2514, oOpen 2524, migrateFx 2528, migrateSnap 2531, invalidate 2550, polyLen 2553, regen 2563, regenAll 2568, applyPreset 2569, varyLane 2587, metric 2603, contextOcc 2604, randLane 2611, hasHits 2648, anchorIds 2652, lhlW 2654, syncOf 2656, patternFeatures 2663, sugTargets 2678, scorePattern 2685, hamming 2695, currentPat 2696, makeSuggestions 2697, applySuggestion 2715, hSnap 2723, hApply 2724, hRecord 2725, hStep 2730, favSnap 2732, favLoad 2734, resetBasis 2741, tuneToKey 2747, resetKit 2749, rollKit 2750, rollLane 2755, patternData 2766, kitData 2767, applyPattern 2768, applyKit 2776
- **AUDIO** (line 2788): noiseBuf 2804, env 2805, noise 2806, mtof 2807, bq 2808, tone 2809, cents 2817, vMem 2819, vBell 2851, pulseBuf 2881, vUdu 2887, vTri 2904, vTabla 2923, vBayan 2940, vWood 2950, vTamb 2962, vClap 2982, vShk 2993, driftAt 3004, chokeIn 3012, voice 3016, voiceKind 3028, vcSpec 3050, vcGet 3057, vcPump 3060
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3070): irKey 3081, makeIR 3082, springIR 3109, unityCurve 3121, satCurve 3122, buildReverb 3123, bloomOn 3135, bloomHz 3136, bloomSync 3137, bloomStep 3140, buildDelay 3141, tapeCurve 3170, NgomaFilterCore 3174, NgomaFilterProc 3242, NgomaRecProc 3255, NgomaCombProc 3263, NgomaShimProc 3277, loadFilter 3292, attachFilter 3300, smooth 3319, mgDecK 3321, mgP 3322, buildMagic 3323, presetTrim 3359, magicSync 3360, magicWorklet 3372, combFallback 3378, resChord 3388, resMsg 3397, resStep 3399, resHz 3401, procSync 3402, combStep 3411, formantStep 3417, glitchStep 3422, cosmosErase 3436, padNotes 3446, padRoot 3455, padLoops 3456, softTone 3465, padSc 3478, padNt 3479, chProgOf 3489, chOn 3490, chPer 3491, chSemi 3492, chDegOf 3493, chWander 3495, chordAt 3500, chName 3502, chKey 3504, chTn 3509, chLabel 3515, tideState 3521, padTides 3533, tideTone 3538, echoPhrase 3547, padEchoes 3553, echoTone 3560, seasonChord 3571, seasonHold 3584, padSeasons 3585, warmVoice 3594, subVoice 3601, grain 3604, padRare 3610, buildPad 3618, padCutHz 3632, unitFlt 3636, fltHz 3637, fltFmt 3638, unitWet 3639, unitEcho 3640, unitTr 3641, trDeg 3642, pmtof 3643, wTry 3646, padTy 3647, padLive 3648, padSync 3649, padDrone 3658, droneVoice 3660, worpSeed 3670, worpSpec 3671, worpCode 3672, worpFlt 3674, worpToken 3675
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3676): lineMine 3688, recOn 3689, midiConnect 3690, midiPadOK 3697, midiDest 3698, midiShort 3699, midiUI 3700, midiQT 3705, midiKey 3708, ngMidi 3710, midiAuto 3715, leadAnchorTpl 3717, leadAnchorFn 3720, leadGain 3722, leadMeasure 3723, buildDub 3733, dubSync 3738, fltQ 3742, buildLead 3743, leadLive 3749, leadSpec 3750, leadSync 3751, leadEngine 3753, leadBar 3763, lcdSet 3770, leadUI 3771, worpBar 3776, worpUI 3791, worpParse 3796, worpUse 3802, worpHash 3804, WBC 3807, ctxEpoch 3808, worpState 3810, worpPost 3813, worpMsg 3818, worpPanel 3843, padBar 3849, buildGraph 3875, buildRoom 3905, roomSync 3910, clipCurve 3912, vetOn 3914, vetAmt 3915, VET_TRIM 3916, masterCurve 3920, buildVet 3921, vetSync 3935, shaperCurve 3939, lfoHz 3941, lfoPeriod 3942, cutPos 3943, cutHz 3944, syncFx 3945, pv 3975, syncGraph 3976, animCurve 3982, animValues 3984, applyAnim 3986, animLive 3992, fxTail 3994, flamGuard 4006, mgQ 4011, scheduleStep 4012, evN 4038, hitGate 4039, AUD 4048, STABLE 4049, loadLate 4050, stableSet 4051, ensureCtx 4054, tick 4055, start 4060, stop 4062, setDrop 4068, setDrumsOff 4071, dropApply 4072, dropMask 4077, preview 4078, $ 4085, mvolGain 4087, setMvol 4088, initMvol 4092, flashLed 4098
- **First visit: invite to press Play, then one next step** (line 4104): onbSave 4107, hintShow 4108, hintHide 4109, onbInit 4110, onbPlayed 4112, onbActed 4113, setPlayUI 4115, clearNow 4116, showDrift 4117, magicGlow 4125
- **Scope: a quiet oscilloscope in the house colours** (line 4132): scopeInit 4136, scopeCalm 4140, scopeCols 4141, scopeHit 4142, scopeWake 4143, scopeGrid 4144, scopeTrace 4147, scopeIdle 4149, scopeFrame 4150, draw 4169, makeSegK 4200, makeSelK 4204, makeKnob 4208, editX 4234, kfoldSeen 4244, kfoldHint 4245, laneRow 4249, paintPending 4329, paintCell 4331, editCell 4347, euRow 4359, renderLanes 4374, renderStyles 4386, initTips 4415, initValues 4430, bindMacro 4431, initControls 4435, status 4710, afterLoad 4711, updHist 4712, renderFavs 4713, inflate 4724, loadShared 4725, fileBase 4730
- **EXPORT: WAV** (line 4735): wavBytes 4737, kCoefs 4749, loudness 4754, truePeak 4764, midiBytes 4770, midiBytesX 4771, chLen 4798, chordMidiBytes 4799, CRC 4806, crc32 4807, zipBlob 4808, loopLen 4828, renderLoop 4830, renderLoopX 4831
- **Capture: keep what you just heard** (line 4840): capAttach 4845, capStart 4853, capLog 4854, capWindow 4855, capAudio 4861, capMidi 4865, capture 4875
- **Delivery: a folder you picked (no zip), or a zip download** (line 4888): idb 4890, kvSet 4891, kvGet 4892, outUI 4893, outPick 4894, outReady 4895, writeFiles 4896, deliver 4898, resampleTo 4904
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 4906): dwKey 4908, dwPrepare 4909
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 4914): jamTrack 4921, jamPut 4922, jamRec 4924, jamStart 4926, jamWorp 4935, jamUI 4938, jamStop 4942, jamWav 4952, jamFiles 4957
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 4964): bbUI 4968, bbPick 4969, bbName 4970, bbSend 4974, exportLoop 4994
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5034): m4lAlign 5037, m4lInit 5041
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5073): onBar 5077, qRun 5081, qMark 5083, qDraw 5086
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5091): scenesRender 5093, sceneStore 5104, sceneClear 5105, sceneRecall 5106
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5109): morphCap 5118, morphStart 5120, morphSet 5129, morphInd 5146, morphSnap 5148, scBase 5152, scEdited 5153, morphStep 5156, morphEnd 5158, morphUI 5166, setView 5178

## Worp: public/worp/index.html (1697 lines)

- **script starts** (line 307): $ 309, mtof 320, mod 321
- **seeded dice** (line 323): rng 324, scaleLabel 335, semis 336
- **patch generation: chance inside musical limits** (line 338): genSpectrum 339, fromHist 353, histEntry 354, genName 355, uniqueName 364, genPatch 365
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 473): anchorFrom 491, euclidW 493, genPhraseStyle 494, rnd01 533, phraseAt 536, phraseAt0 538, phCx 546, phZ 547, phraseCore 548, phraseDesc 583
- **the modular part: sources, cables, re-patching** (line 585): genMods 588, genFx 640, fxDesc 668, destRange 677, destName 689, srcDesc 690
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 699): NgomaFilterCore 702, NgomaFilterProc 770, WorpRecProc 781, cutHz 795, loadFilter 796, syncFilter 803, saveFilter 807, saveEnv 810
- **audio graph** (line 812): makeIR 814, curve 827, initAudio 828, gateStep 865, prepWaves 867, applyFx 874, mixVal 896, applyMix 897, loopD 899, airNorm 900, foldCurve 901, bitCurve 904, quantCurve 905, chroma 906, fxRotor 913, fxBitplane 921, fxHalo 928, fxStrings 946, fxShifter 954, fxSonar 968, buildFx 978, retireFx 986, globalParams 990, buildMods 991, retireMods 1012, modTick 1018, envMul 1054, ampOf 1055, Voice 1058
- **voices** (line 1173): polyOn 1175, polyOff 1180, mono 1181, playRec 1187, playPhrase 1191, releaseAll 1194, liveOn 1200, liveOff 1210, setSustain 1223
- **state** (line 1225): cur 1227, getBpm 1228, newSeed 1229, load 1230, save 1231, setPatch 1233, roll 1248, back 1253, setMode 1257
- **playing by itself** (line 1271): startDrone 1273, evolveDrone 1274, tick 1282, startPlay 1293, stopPlay 1304
- **MIDI** (line 1311): midiStatus 1313, initMIDI 1314, onMidi 1322, renderLearn 1339
- **rendering** (line 1346): noteName 1347, layerDetail 1348, layerTag 1355
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1357): BC 1362, ngomaOpen 1363, linked 1368, outGain 1370, epochToCtx 1371, hostT0 1374, relock 1375, transportSync 1377, worpPost 1385, setPlayUI 1386, hostVoicing 1391, applyHost 1393, hostChanged 1395, renderFollow 1402, focusNgoma 1405, toNgoma 1409, onHostMsg 1410, recStart 1426, recStop 1430, patchCode 1435, fltTok 1438, shareToken 1439, setFLT 1440, setENV 1441, envTok 1442, envNeutral 1443, hearInNgoma 1449, renderLive 1452, parseToken 1455, render 1459, renderFx 1485, renderPatch 1491, renderMusic 1500, lineHas 1517, lineUI 1518, lineSet 1520, drawSteps 1524, recLine 1533, recQ 1541, recFinish 1542, kbStart 1552, buildKb 1553, markKey 1561, ptrUp 1565, togglePlay 1580
- **ring visual** (line 1590): ringAn 1594, draw 1595
- **wiring** (line 1619): renderFilter 1639, secT 1648, renderEnv 1649
