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

## Ngoma: public/index.html (5216 lines)

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
- **ENGINE** (line 2113): isMan 2139, kickOn 2140, kickHeld 2141, rnd 2314, euclid 2319, charOf 2324, genSteps 2325, varWeight 2352, mutateSteps 2353, mutateStepsX 2354, variant 2388, anySolo 2393, fillOn 2395, condOk 2397, dlgPalette 2412, dlgPlan 2414, lifeInfo 2438, eventsAt 2445, stepDur 2476, grooveOff 2480, hitsOf 2490, midiNote 2495, mname 2503, inScale 2504, snap 2505, nearestPC 2506
- **STATE** (line 2509): panMig 2515, freshLane 2519, lanesFrom 2526, oOpen 2536, migrateFx 2540, migrateSnap 2543, invalidate 2562, polyLen 2565, regen 2575, regenAll 2580, applyPreset 2581, varyLane 2599, metric 2615, contextOcc 2616, randLane 2623, hasHits 2660, anchorIds 2664, lhlW 2666, syncOf 2668, patternFeatures 2675, sugTargets 2690, scorePattern 2697, hamming 2707, currentPat 2708, makeSuggestions 2709, applySuggestion 2727, hSnap 2735, hApply 2736, hRecord 2737, hStep 2742, favSnap 2744, favLoad 2746, resetBasis 2753, tuneToKey 2759, resetKit 2761, rollKit 2762, rollLane 2767, patternData 2778, kitData 2779, applyPattern 2780, applyKit 2788
- **AUDIO** (line 2800): noiseBuf 2816, env 2817, noise 2818, mtof 2819, bq 2820, tone 2821, cents 2829, vMem 2831, vBell 2863, pulseBuf 2893, vUdu 2899, vTri 2916, vTabla 2935, vBayan 2952, vWood 2962, vTamb 2974, vClap 2994, vShk 3005, driftAt 3016, chokeIn 3024, voice 3028, voiceKind 3040, vcSpec 3062, vcGet 3069, vcPump 3072
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3082): irKey 3093, makeIR 3094, springIR 3121, unityCurve 3133, satCurve 3134, buildReverb 3135, bloomOn 3147, bloomHz 3148, bloomSync 3149, bloomStep 3152, buildDelay 3153, tapeCurve 3182, NgomaFilterCore 3186, NgomaFilterProc 3254, NgomaRecProc 3267, NgomaCombProc 3275, NgomaShimProc 3289, loadFilter 3304, attachFilter 3312, smooth 3331, mgDecK 3333, mgP 3334, buildMagic 3335, presetTrim 3371, magicSync 3372, magicWorklet 3384, combFallback 3390, resChord 3400, resMsg 3409, resStep 3411, resHz 3413, procSync 3414, combStep 3426, formantStep 3432, glitchStep 3437, cosmosErase 3451, padNotes 3461, padRoot 3470, padLoops 3471, softTone 3480, padSc 3493, padNt 3494, chProgOf 3504, chOn 3505, chPer 3506, chSemi 3507, chDegOf 3508, chWander 3510, chordAt 3515, chName 3517, chKey 3519, chTn 3524, chLabel 3530, tideState 3536, padTides 3548, tideTone 3553, echoPhrase 3562, padEchoes 3568, echoTone 3575, seasonChord 3586, seasonHold 3599, padSeasons 3600, warmVoice 3609, subVoice 3616, grain 3619, padRare 3625, buildPad 3633, padCutHz 3647, unitFlt 3651, fltHz 3652, fltFmt 3653, unitWet 3654, unitEcho 3655, unitTr 3656, trDeg 3657, pmtof 3658, wTry 3661, padTy 3662, padLive 3663, padSync 3664, padDrone 3673, droneVoice 3675, worpSeed 3685, worpSpec 3686, worpCode 3687, worpFlt 3689, worpToken 3690
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3691): lineMine 3703, recOn 3704, midiConnect 3705, midiPadOK 3712, midiDest 3713, midiShort 3714, midiUI 3715, midiQT 3720, midiKey 3723, ngMidi 3725, midiAuto 3730, leadAnchorTpl 3732, leadAnchorFn 3735, leadGain 3737, leadMeasure 3738, buildDub 3748, dubSync 3753, fltQ 3757, buildLead 3758, leadLive 3764, leadSpec 3765, leadSync 3766, leadEngine 3768, leadBar 3778, lcdSet 3785, leadUI 3786, worpBar 3791, worpUI 3806, worpParse 3811, worpUse 3817, worpHash 3819, WBC 3822, ctxEpoch 3823, worpState 3825, worpPost 3828, worpMsg 3833, worpPanel 3858, padBar 3864, buildGraph 3890, buildRoom 3920, roomSync 3925, clipCurve 3927, vetOn 3929, vetAmt 3930, VET_TRIM 3931, masterCurve 3935, buildVet 3936, vetSync 3950, shaperCurve 3954, lfoHz 3956, lfoPeriod 3957, cutPos 3958, cutHz 3959, syncFx 3960, pv 3990, syncGraph 3991, animCurve 3997, animValues 3999, applyAnim 4001, animLive 4007, fxTail 4009, flamGuard 4021, mgQ 4026, scheduleStep 4027, evN 4053, hitGate 4054, AUD 4063, STABLE 4064, loadLate 4065, stableSet 4066, ensureCtx 4069, tick 4070, start 4075, stop 4077, setDrop 4083, setDrumsOff 4086, dropApply 4087, dropMask 4092, preview 4093, $ 4100, mvolGain 4102, setMvol 4103, initMvol 4107, flashLed 4113
- **First visit: invite to press Play, then one next step** (line 4119): onbSave 4122, hintShow 4123, hintHide 4124, onbInit 4125, onbPlayed 4127, onbActed 4128, setPlayUI 4130, clearNow 4131, showDrift 4132, magicGlow 4140
- **Scope: a quiet oscilloscope in the house colours** (line 4147): scopeInit 4151, scopeCalm 4155, scopeCols 4156, scopeHit 4157, scopeWake 4158, scopeGrid 4159, scopeTrace 4162, scopeIdle 4164, scopeFrame 4165, draw 4184, makeSegK 4215, makeSelK 4219, makeKnob 4223, editX 4249, kfoldSeen 4259, kfoldHint 4260, laneRow 4264, paintPending 4344, paintCell 4346, editCell 4362, euRow 4374, renderLanes 4389, renderStyles 4401, initTips 4430, initValues 4445, bindMacro 4446, initControls 4450, status 4733, afterLoad 4734, updHist 4735, renderFavs 4736, inflate 4747, loadShared 4748, fileBase 4753
- **EXPORT: WAV** (line 4758): wavBytes 4760, kCoefs 4772, loudness 4777, truePeak 4787, midiBytes 4793, midiBytesX 4794, chLen 4821, chordMidiBytes 4822, CRC 4829, crc32 4830, zipBlob 4831, loopLen 4851, renderLoop 4853, renderLoopX 4854
- **Capture: keep what you just heard** (line 4863): capAttach 4868, capStart 4876, capLog 4877, capWindow 4878, capAudio 4884, capMidi 4888, capture 4898
- **Delivery: a folder you picked (no zip), or a zip download** (line 4911): idb 4913, kvSet 4914, kvGet 4915, outUI 4916, outPick 4917, outReady 4918, writeFiles 4919, deliver 4921, resampleTo 4927
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 4929): dwKey 4931, dwPrepare 4932
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 4937): jamTrack 4944, jamPut 4945, jamRec 4947, jamStart 4949, jamWorp 4958, jamUI 4961, jamStop 4965, jamWav 4975, jamFiles 4980
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 4987): bbUI 4991, bbPick 4992, bbName 4993, bbSend 4997, exportLoop 5017
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5057): m4lAlign 5060, m4lInit 5064
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5096): onBar 5100, qRun 5104, qMark 5106, qDraw 5109
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5114): scenesRender 5116, sceneStore 5127, sceneClear 5128, sceneRecall 5129
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5132): morphCap 5141, morphStart 5143, morphSet 5152, morphInd 5169, morphSnap 5171, scBase 5175, scEdited 5176, morphStep 5179, morphEnd 5181, morphUI 5189, setView 5201

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
