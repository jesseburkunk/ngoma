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

## Ngoma: public/index.html (5318 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 430): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 455): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 473): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 483): (no functions)
- **Scenes (v91)** (line 495): (no functions)
- **Changes on the next bar (v88)** (line 521): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 531): (no functions)
- **script starts** (line 1256): mtof 1271, mod 1272
- **seeded dice** (line 1274): rng 1275, scaleLabel 1286, semis 1287
- **patch generation: chance inside musical limits** (line 1289): genSpectrum 1290, fromHist 1304, histEntry 1305, genName 1306, uniqueName 1315, genPatch 1316
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1424): anchorFrom 1442, euclidW 1444, genPhraseStyle 1445, rnd01 1484, phraseAt 1487, phraseAt0 1489, phCx 1497, phZ 1498, phraseCore 1499, phraseDesc 1534
- **the modular part: sources, cables, re-patching** (line 1536): genMods 1539, genFx 1591, fxDesc 1619, destRange 1628, destName 1640, srcDesc 1641, create 1651, makeIR 1658, curve 1671, initGraph 1672, gateStep 1703, prepWaves 1705, applyFx 1712, mixVal 1734, applyMix 1735, loopD 1737, airNorm 1738, foldCurve 1739, bitCurve 1742, quantCurve 1743, chroma 1744, fxRotor 1751, fxBitplane 1759, fxHalo 1766, fxStrings 1784, fxShifter 1792, fxSonar 1806, buildFx 1816, retireFx 1824, globalParams 1828, buildMods 1829, retireMods 1850, modTick 1856, envMul 1892, ampOf 1893, Voice 1896
- **voices** (line 2011): polyOn 2013, polyOff 2018, mono 2019, playRec 2025, playPhrase 2029, releaseAll 2032
- **script starts** (line 2094): (no functions)
- **ENGINE** (line 2120): isMan 2146, kickOn 2147, kickHeld 2148, rnd 2321, euclid 2326, charOf 2331, genSteps 2332, varWeight 2359, mutateSteps 2360, mutateStepsX 2361, variant 2395, anySolo 2400, fillOn 2402, condOk 2404, dlgPalette 2419, dlgPlan 2421, lifeInfo 2445, eventsAt 2452, stepDur 2483, grooveOff 2487, hitsOf 2497, midiNote 2502, mname 2510, inScale 2511, snap 2512, nearestPC 2513
- **STATE** (line 2516): panMig 2522, freshLane 2526, lanesFrom 2533, oOpen 2543, migrateFx 2547, migrateSnap 2550, invalidate 2569, polyLen 2572, regen 2582, regenAll 2587, applyPreset 2588, varyLane 2606, metric 2622, contextOcc 2623, randLane 2630, hasHits 2667, anchorIds 2671, lhlW 2673, syncOf 2675, patternFeatures 2682, sugTargets 2697, scorePattern 2704, hamming 2714, currentPat 2715, makeSuggestions 2716, applySuggestion 2734, hSnap 2742, hApply 2743, hRecord 2744, hStep 2749, favSnap 2751, favLoad 2753, resetBasis 2760, tuneToKey 2766, resetKit 2768, rollKit 2769, rollLane 2774, patternData 2785, kitData 2786, applyPattern 2787, applyKit 2795
- **AUDIO** (line 2807): noiseBuf 2823, env 2824, noise 2825, mtof 2826, bq 2827, tone 2828, cents 2836, vMem 2838, vBell 2870, pulseBuf 2900, vUdu 2906, vTri 2923, vTabla 2942, vBayan 2959, vWood 2969, vTamb 2981, vClap 3001, vShk 3012, driftAt 3023, chokeIn 3031, voice 3035, voiceKind 3047, vcSpec 3069, vcGet 3076, vcPump 3079
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3089): irKey 3100, makeIR 3101, springIR 3128, unityCurve 3140, satCurve 3141, buildReverb 3142, bloomOn 3154, bloomHz 3155, bloomSync 3156, bloomStep 3159, buildDelay 3160, tapeCurve 3189, NgomaFilterCore 3193, NgomaFilterProc 3261, NgomaRecProc 3274, NgomaCombProc 3282, NgomaShimProc 3296, loadFilter 3311, attachFilter 3319, smooth 3338, mgDecK 3340, mgP 3341, buildMagic 3342, presetTrim 3378, magicSync 3379, magicWorklet 3391, combFallback 3397, resChord 3407, resMsg 3416, resStep 3418, resHz 3420, procSync 3421, combStep 3433, formantStep 3439, glitchStep 3444, cosmosErase 3458, padNotes 3468, padRoot 3477, padLoops 3478, softTone 3487, padSc 3500, padNt 3501, chProgOf 3511, chOn 3512, chPer 3513, chSemi 3514, chDegOf 3515, chWander 3517, chordAt 3522, chName 3524, chKey 3526, chTn 3531, chLabel 3537, tideState 3543, padTides 3555, tideTone 3560, echoPhrase 3569, padEchoes 3575, echoTone 3582, seasonChord 3593, seasonHold 3606, padSeasons 3607, warmVoice 3616, subVoice 3623, grain 3626, padRare 3632, buildPad 3640, padCutHz 3655, unitFlt 3659, fltHz 3660, fltFmt 3661, unitWet 3662, unitEcho 3663, unitTr 3664, trDeg 3665, pmtof 3666, wTry 3669, padTy 3670, padLive 3671, padSync 3672, padDrone 3685, droneVoice 3687, worpSeed 3697, worpSpec 3698, worpCode 3699, worpFlt 3701, worpToken 3702
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3703): lineMine 3715, recOn 3716, midiConnect 3717, midiPadOK 3724, midiDest 3725, midiShort 3726, midiUI 3727, midiQT 3732, midiKey 3735, ngMidi 3737, midiAuto 3742, leadAnchorTpl 3744, leadAnchorFn 3747, leadGain 3749, leadMeasure 3750, buildDub 3760, dubSync 3765, fltQ 3769, buildLead 3770
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3776): fldTrim 3791, fldId 3792, fldInfo 3793, fldKey 3794, fldBuf 3795, fldNorm 3796, fldDecode 3798, fldLoad 3799, fldOwnLoad 3808, fldOwnSet 3810, buildField 3811, fldLive 3815, fldHz 3816, fldStopLoop 3817, fldSync 3818, fldWalk 3825, fldStep 3826, fldDuck 3838, fldUI 3839, leadLive 3843, leadSpec 3844, leadSync 3845, leadEngine 3847, leadBar 3857, lcdSet 3864, leadUI 3865, worpBar 3870, worpUI 3885, worpParse 3890, worpUse 3896, worpHash 3898, WBC 3901, ctxEpoch 3902, worpState 3904, worpPost 3907, worpMsg 3912, worpPanel 3937, padBar 3943, buildGraph 3969, buildRoom 3999, roomSync 4004, clipCurve 4006, vetOn 4008, vetAmt 4009, VET_TRIM 4010, masterCurve 4014, buildVet 4015, vetSync 4029, shaperCurve 4033, lfoHz 4035, lfoPeriod 4036, cutPos 4037, cutHz 4038, syncFx 4039, pv 4069, syncGraph 4070, animCurve 4076, animValues 4078, applyAnim 4080, animLive 4086, fxTail 4088, flamGuard 4101, mgQ 4106, scheduleStep 4107, evN 4133, hitGate 4134, AUD 4143, STABLE 4144, loadLate 4145, stableSet 4146, ensureCtx 4149, tick 4150, start 4155, stop 4157, setDrop 4163, setDrumsOff 4166, dropApply 4167, dropMask 4172, preview 4173, $ 4180, mvolGain 4182, setMvol 4183, initMvol 4187, flashLed 4193
- **First visit: invite to press Play, then one next step** (line 4199): onbSave 4202, hintShow 4203, hintHide 4204, onbInit 4205, onbPlayed 4207, onbActed 4208, setPlayUI 4210, clearNow 4211, showDrift 4212, magicGlow 4220
- **Scope: a quiet oscilloscope in the house colours** (line 4227): scopeInit 4231, scopeCalm 4235, scopeCols 4236, scopeHit 4237, scopeWake 4238, scopeGrid 4239, scopeTrace 4242, scopeIdle 4244, scopeFrame 4245, draw 4264, makeSegK 4295, makeSelK 4299, makeKnob 4303, editX 4329, kfoldSeen 4339, kfoldHint 4340, laneRow 4344, paintPending 4424, paintCell 4426, editCell 4442, euRow 4454, renderLanes 4469, renderStyles 4481, initTips 4510, initValues 4525, bindMacro 4526, initControls 4530, status 4834, afterLoad 4835, updHist 4836, renderFavs 4837, inflate 4848, loadShared 4849, fileBase 4854
- **EXPORT: WAV** (line 4859): wavBytes 4861, kCoefs 4873, loudness 4878, truePeak 4888, midiBytes 4894, midiBytesX 4895, chLen 4922, chordMidiBytes 4923, CRC 4930, crc32 4931, zipBlob 4932, loopLen 4952, renderLoop 4954, renderLoopX 4955
- **Capture: keep what you just heard** (line 4964): capAttach 4969, capStart 4977, capLog 4978, capWindow 4979, capAudio 4985, capMidi 4989, capture 4999
- **Delivery: a folder you picked (no zip), or a zip download** (line 5012): idb 5014, kvSet 5015, kvGet 5016, outUI 5017, outPick 5018, outReady 5019, writeFiles 5020, deliver 5022, resampleTo 5028
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5030): dwKey 5032, dwPrepare 5033
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5038): jamTrack 5045, jamPut 5046, jamRec 5048, jamStart 5050, jamWorp 5059, jamUI 5062, jamStop 5066, jamWav 5076, jamFiles 5081
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5088): bbUI 5092, bbPick 5093, bbName 5094, bbSend 5098, exportLoop 5118
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5159): m4lAlign 5162, m4lInit 5166
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5198): onBar 5202, qRun 5206, qMark 5208, qDraw 5211
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5216): scenesRender 5218, sceneStore 5229, sceneClear 5230, sceneRecall 5231
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5234): morphCap 5243, morphStart 5245, morphSet 5254, morphInd 5271, morphSnap 5273, scBase 5277, scEdited 5278, morphStep 5281, morphEnd 5283, morphUI 5291, setView 5303

## Worp: public/worp/index.html (1840 lines)

- **script starts** (line 445): $ 447, mtof 458, mod 459
- **seeded dice** (line 461): rng 462, scaleLabel 473, semis 474
- **patch generation: chance inside musical limits** (line 476): genSpectrum 477, fromHist 491, histEntry 492, genName 493, uniqueName 502, genPatch 503
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 611): anchorFrom 629, euclidW 631, genPhraseStyle 632, rnd01 671, phraseAt 674, phraseAt0 676, phCx 684, phZ 685, phraseCore 686, phraseDesc 721
- **the modular part: sources, cables, re-patching** (line 723): genMods 726, genFx 778, fxDesc 806, destRange 815, destName 827, srcDesc 828
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 837): NgomaFilterCore 840, NgomaFilterProc 908, WorpRecProc 919, cutHz 933, loadFilter 934, syncFilter 941, saveFilter 945, saveEnv 948
- **audio graph** (line 950): makeIR 952, curve 965, initAudio 966, gateStep 1003, prepWaves 1005, applyFx 1012, mixVal 1034, applyMix 1035, loopD 1037, airNorm 1038, foldCurve 1039, bitCurve 1042, quantCurve 1043, chroma 1044, fxRotor 1051, fxBitplane 1059, fxHalo 1066, fxStrings 1084, fxShifter 1092, fxSonar 1106, buildFx 1116, retireFx 1124, globalParams 1128, buildMods 1129, retireMods 1150, modTick 1156, envMul 1192, ampOf 1193, Voice 1196
- **voices** (line 1311): polyOn 1313, polyOff 1318, mono 1319, playRec 1325, playPhrase 1329, releaseAll 1332, liveOn 1338, liveOff 1348, setSustain 1361
- **state** (line 1363): cur 1365, getBpm 1366, newSeed 1367, load 1368, save 1369, setPatch 1371, roll 1386, back 1391, setMode 1395
- **playing by itself** (line 1409): startDrone 1411, evolveDrone 1412, tick 1420, startPlay 1431, stopPlay 1442
- **MIDI** (line 1449): midiStatus 1451, initMIDI 1452, onMidi 1460, renderLearn 1477
- **rendering** (line 1484): noteName 1485, layerDetail 1486, layerTag 1493
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1495): BC 1500, ngomaOpen 1501, linked 1506, outGain 1508, epochToCtx 1509, hostT0 1512, relock 1513, transportSync 1515, worpPost 1523, setPlayUI 1524, hostVoicing 1529, applyHost 1531, hostChanged 1533, renderFollow 1540, focusNgoma 1543, toNgoma 1547, onHostMsg 1548, recStart 1564, recStop 1568, patchCode 1573, fltTok 1576, shareToken 1577, setFLT 1578, setENV 1579, envTok 1580, envNeutral 1581, hearInNgoma 1587, renderLive 1590, parseToken 1593, render 1597, renderFx 1623, renderPatch 1629, renderMusic 1638, lineHas 1655, lineUI 1656, lineSet 1658, drawSteps 1662, recLine 1671, recQ 1679, recFinish 1680, kbStart 1690, buildKb 1691, markKey 1699, ptrUp 1703, togglePlay 1718
- **ring visual** (line 1728): ringAn 1732, draw 1733
- **wiring** (line 1757): renderFilter 1777, secT 1786, renderEnv 1787, fillRange 1833
