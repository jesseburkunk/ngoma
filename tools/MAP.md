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

## Ngoma: public/index.html (5151 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 429): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 454): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 472): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 482): (no functions)
- **Scenes (v91)** (line 494): (no functions)
- **Changes on the next bar (v88)** (line 520): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 530): (no functions)
- **script starts** (line 1244): mtof 1259, mod 1260
- **seeded dice** (line 1262): rng 1263, scaleLabel 1274, semis 1275
- **patch generation: chance inside musical limits** (line 1277): genSpectrum 1278, fromHist 1292, histEntry 1293, genName 1294, uniqueName 1303, genPatch 1304
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1406): anchorFrom 1422, euclidW 1424, genPhraseStyle 1425, rnd01 1458, phraseAt 1461, phraseAt0 1463, phCx 1471, phZ 1472, phraseCore 1473, phraseDesc 1503
- **the modular part: sources, cables, re-patching** (line 1505): genMods 1508, genFx 1560, fxDesc 1588, destRange 1597, destName 1609, srcDesc 1610, create 1620, makeIR 1627, curve 1640, initGraph 1641, gateStep 1672, prepWaves 1674, applyFx 1681, mixVal 1703, applyMix 1704, loopD 1706, airNorm 1707, foldCurve 1708, bitCurve 1711, quantCurve 1712, chroma 1713, fxRotor 1720, fxBitplane 1728, fxHalo 1735, fxStrings 1753, fxShifter 1761, fxSonar 1775, buildFx 1785, retireFx 1793, globalParams 1797, buildMods 1798, retireMods 1819, modTick 1825, envMul 1861, ampOf 1862, Voice 1865
- **voices** (line 1980): polyOn 1982, polyOff 1987, mono 1988, playRec 1994, playPhrase 1998, releaseAll 2001
- **script starts** (line 2063): (no functions)
- **ENGINE** (line 2089): isMan 2115, kickOn 2116, kickHeld 2117, rnd 2269, euclid 2274, charOf 2279, genSteps 2280, varWeight 2307, mutateSteps 2308, mutateStepsX 2309, variant 2343, anySolo 2348, fillOn 2350, condOk 2352, dlgPalette 2367, dlgPlan 2369, lifeInfo 2393, eventsAt 2400, stepDur 2431, grooveOff 2435, hitsOf 2445, midiNote 2450, mname 2458, inScale 2459, snap 2460, nearestPC 2461
- **STATE** (line 2464): panMig 2470, freshLane 2474, lanesFrom 2481, oOpen 2491, migrateFx 2495, migrateSnap 2498, invalidate 2517, polyLen 2520, regen 2529, regenAll 2534, applyPreset 2535, varyLane 2553, metric 2569, contextOcc 2570, randLane 2577, hasHits 2614, anchorIds 2618, lhlW 2620, syncOf 2622, patternFeatures 2629, sugTargets 2644, scorePattern 2651, hamming 2661, currentPat 2662, makeSuggestions 2663, applySuggestion 2681, hSnap 2689, hApply 2690, hRecord 2691, hStep 2696, favSnap 2698, favLoad 2700, resetBasis 2707, tuneToKey 2713, resetKit 2715, rollKit 2716, rollLane 2721, patternData 2732, kitData 2733, applyPattern 2734, applyKit 2742
- **AUDIO** (line 2754): noiseBuf 2770, env 2771, noise 2772, mtof 2773, bq 2774, tone 2775, cents 2783, vMem 2785, vBell 2817, pulseBuf 2847, vUdu 2853, vTri 2870, vTabla 2889, vBayan 2906, vWood 2916, vTamb 2928, vClap 2948, vShk 2959, driftAt 2970, chokeIn 2978, voice 2982, voiceKind 2994, vcSpec 3016, vcGet 3023, vcPump 3026
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3036): irKey 3047, makeIR 3048, springIR 3075, unityCurve 3087, satCurve 3088, buildReverb 3089, bloomOn 3101, bloomHz 3102, bloomSync 3103, bloomStep 3106, buildDelay 3107, tapeCurve 3136, NgomaFilterCore 3140, NgomaFilterProc 3208, NgomaRecProc 3221, NgomaCombProc 3229, NgomaShimProc 3243, loadFilter 3258, attachFilter 3266, smooth 3285, mgDecK 3287, mgP 3288, buildMagic 3289, presetTrim 3325, magicSync 3326, magicWorklet 3338, combFallback 3344, resChord 3354, resMsg 3363, resStep 3365, resHz 3367, procSync 3368, combStep 3377, formantStep 3383, glitchStep 3388, cosmosErase 3402, padNotes 3412, padRoot 3421, padLoops 3422, softTone 3431, padSc 3444, padNt 3445, chProgOf 3455, chOn 3456, chPer 3457, chSemi 3458, chDegOf 3459, chWander 3461, chordAt 3466, chName 3468, chKey 3470, chTn 3475, chLabel 3481, tideState 3487, padTides 3499, tideTone 3504, echoPhrase 3513, padEchoes 3519, echoTone 3526, seasonChord 3537, seasonHold 3550, padSeasons 3551, warmVoice 3560, subVoice 3567, grain 3570, padRare 3576, buildPad 3584, padCutHz 3598, unitFlt 3602, fltHz 3603, fltFmt 3604, unitWet 3605, unitEcho 3606, unitTr 3607, trDeg 3608, pmtof 3609, wTry 3612, padTy 3613, padLive 3614, padSync 3615, padDrone 3624, droneVoice 3626, worpSeed 3636, worpSpec 3637, worpCode 3638, worpFlt 3640, worpToken 3641
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3642): lineMine 3654, recOn 3655, midiConnect 3656, midiPadOK 3663, midiDest 3664, midiShort 3665, midiUI 3666, midiQT 3671, midiKey 3674, ngMidi 3676, midiAuto 3681, leadAnchorTpl 3683, leadAnchorFn 3686, leadGain 3688, leadMeasure 3689, buildDub 3699, dubSync 3704, fltQ 3708, buildLead 3709, leadLive 3710, leadSpec 3711, leadSync 3712, leadEngine 3714, leadBar 3724, lcdSet 3731, leadUI 3732, worpBar 3737, worpUI 3752, worpParse 3757, worpUse 3763, worpHash 3765, WBC 3768, ctxEpoch 3769, worpState 3771, worpPost 3774, worpMsg 3779, worpPanel 3804, padBar 3810, buildGraph 3836, buildRoom 3866, roomSync 3871, clipCurve 3873, vetOn 3875, vetAmt 3876, VET_TRIM 3877, masterCurve 3881, buildVet 3882, vetSync 3896, shaperCurve 3900, lfoHz 3902, lfoPeriod 3903, cutPos 3904, cutHz 3905, syncFx 3906, pv 3936, syncGraph 3937, animCurve 3943, animValues 3945, applyAnim 3947, animLive 3953, fxTail 3955, flamGuard 3967, mgQ 3972, scheduleStep 3973, evN 3999, hitGate 4000, STABLE 4008, loadLate 4009, stableSet 4010, ensureCtx 4013, tick 4014, start 4019, stop 4021, setDrop 4027, setDrumsOff 4030, dropApply 4031, dropMask 4036, preview 4037, $ 4044, mvolGain 4046, setMvol 4047, initMvol 4051, flashLed 4057
- **First visit: invite to press Play, then one next step** (line 4063): onbSave 4066, hintShow 4067, hintHide 4068, onbInit 4069, onbPlayed 4071, onbActed 4072, setPlayUI 4074, clearNow 4075, showDrift 4076, magicGlow 4084
- **Scope: a quiet oscilloscope in the house colours** (line 4091): scopeInit 4095, scopeCalm 4099, scopeCols 4100, scopeHit 4101, scopeWake 4102, scopeGrid 4103, scopeTrace 4106, scopeIdle 4108, scopeFrame 4109, draw 4128, makeSegK 4159, makeSelK 4163, makeKnob 4167, editX 4193, kfoldSeen 4203, kfoldHint 4204, laneRow 4208, paintPending 4288, paintCell 4290, editCell 4306, euRow 4318, renderLanes 4333, renderStyles 4345, initTips 4374, initValues 4389, bindMacro 4390, initControls 4394, status 4668, afterLoad 4669, updHist 4670, renderFavs 4671, inflate 4682, loadShared 4683, fileBase 4688
- **EXPORT: WAV** (line 4693): wavBytes 4695, kCoefs 4707, loudness 4712, truePeak 4722, midiBytes 4728, midiBytesX 4729, chLen 4756, chordMidiBytes 4757, CRC 4764, crc32 4765, zipBlob 4766, loopLen 4786, renderLoop 4788, renderLoopX 4789
- **Capture: keep what you just heard** (line 4798): capAttach 4803, capStart 4811, capLog 4812, capWindow 4813, capAudio 4819, capMidi 4823, capture 4833
- **Delivery: a folder you picked (no zip), or a zip download** (line 4846): idb 4848, kvSet 4849, kvGet 4850, outUI 4851, outPick 4852, outReady 4853, writeFiles 4854, deliver 4856, resampleTo 4862
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 4864): dwKey 4866, dwPrepare 4867
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 4872): jamTrack 4879, jamPut 4880, jamRec 4882, jamStart 4884, jamWorp 4893, jamUI 4896, jamStop 4900, jamWav 4910, jamFiles 4915
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 4922): bbUI 4926, bbPick 4927, bbName 4928, bbSend 4932, exportLoop 4952
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 4992): m4lAlign 4995, m4lInit 4999
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5031): onBar 5035, qRun 5039, qMark 5041, qDraw 5044
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5049): scenesRender 5051, sceneStore 5062, sceneClear 5063, sceneRecall 5064
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5067): morphCap 5076, morphStart 5078, morphSet 5087, morphInd 5104, morphSnap 5106, scBase 5110, scEdited 5111, morphStep 5114, morphEnd 5116, morphUI 5124, setView 5136

## Worp: public/worp/index.html (1678 lines)

- **script starts** (line 307): $ 309, mtof 320, mod 321
- **seeded dice** (line 323): rng 324, scaleLabel 335, semis 336
- **patch generation: chance inside musical limits** (line 338): genSpectrum 339, fromHist 353, histEntry 354, genName 355, uniqueName 364, genPatch 365
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 467): anchorFrom 483, euclidW 485, genPhraseStyle 486, rnd01 519, phraseAt 522, phraseAt0 524, phCx 532, phZ 533, phraseCore 534, phraseDesc 564
- **the modular part: sources, cables, re-patching** (line 566): genMods 569, genFx 621, fxDesc 649, destRange 658, destName 670, srcDesc 671
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 680): NgomaFilterCore 683, NgomaFilterProc 751, WorpRecProc 762, cutHz 776, loadFilter 777, syncFilter 784, saveFilter 788, saveEnv 791
- **audio graph** (line 793): makeIR 795, curve 808, initAudio 809, gateStep 846, prepWaves 848, applyFx 855, mixVal 877, applyMix 878, loopD 880, airNorm 881, foldCurve 882, bitCurve 885, quantCurve 886, chroma 887, fxRotor 894, fxBitplane 902, fxHalo 909, fxStrings 927, fxShifter 935, fxSonar 949, buildFx 959, retireFx 967, globalParams 971, buildMods 972, retireMods 993, modTick 999, envMul 1035, ampOf 1036, Voice 1039
- **voices** (line 1154): polyOn 1156, polyOff 1161, mono 1162, playRec 1168, playPhrase 1172, releaseAll 1175, liveOn 1181, liveOff 1191, setSustain 1204
- **state** (line 1206): cur 1208, getBpm 1209, newSeed 1210, load 1211, save 1212, setPatch 1214, roll 1229, back 1234, setMode 1238
- **playing by itself** (line 1252): startDrone 1254, evolveDrone 1255, tick 1263, startPlay 1274, stopPlay 1285
- **MIDI** (line 1292): midiStatus 1294, initMIDI 1295, onMidi 1303, renderLearn 1320
- **rendering** (line 1327): noteName 1328, layerDetail 1329, layerTag 1336
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1338): BC 1343, ngomaOpen 1344, linked 1349, outGain 1351, epochToCtx 1352, hostT0 1355, relock 1356, transportSync 1358, worpPost 1366, setPlayUI 1367, hostVoicing 1372, applyHost 1374, hostChanged 1376, renderFollow 1383, focusNgoma 1386, toNgoma 1390, onHostMsg 1391, recStart 1407, recStop 1411, patchCode 1416, fltTok 1419, shareToken 1420, setFLT 1421, setENV 1422, envTok 1423, envNeutral 1424, hearInNgoma 1430, renderLive 1433, parseToken 1436, render 1440, renderFx 1466, renderPatch 1472, renderMusic 1481, lineHas 1498, lineUI 1499, lineSet 1501, drawSteps 1505, recLine 1514, recQ 1522, recFinish 1523, kbStart 1533, buildKb 1534, markKey 1542, ptrUp 1546, togglePlay 1561
- **ring visual** (line 1571): ringAn 1575, draw 1576
- **wiring** (line 1600): renderFilter 1620, secT 1629, renderEnv 1630
