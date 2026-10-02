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

## Ngoma: public/index.html (5543 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1265): mtof 1280, mod 1281
- **seeded dice** (line 1283): rng 1284, scaleLabel 1295, semis 1296
- **patch generation: chance inside musical limits** (line 1298): genSpectrum 1299, fromHist 1313, histEntry 1314, genName 1315, uniqueName 1324, genPatch 1325
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1448): anchorFrom 1466, euclidW 1468, genPhraseStyle 1469, rnd01 1508, phraseAt 1511, phraseAt0 1513, phCx 1521, phZ 1522, phraseCore 1523, phraseDesc 1558, lvSd 1567, lvMem 1568, lvP2 1573, lvCt 1574, lvSnap 1575, lvBar 1576, phraseV2 1592, phraseOut 1600
- **the modular part: sources, cables, re-patching** (line 1602): genMods 1605, genFx 1657, fxDesc 1685, destRange 1694, destName 1706, srcDesc 1707, create 1717, makeIR 1724, curve 1737, initGraph 1738, gateStep 1769, prepWaves 1771, applyFx 1778, mixVal 1800, applyMix 1801, loopD 1803, airNorm 1804, foldCurve 1805, bitCurve 1808, quantCurve 1809, chroma 1810, fxRotor 1817, fxBitplane 1825, fxHalo 1832, fxStrings 1850, fxShifter 1858, fxSonar 1872, buildFx 1882, retireFx 1890, globalParams 1894, buildMods 1895, retireMods 1916, modTick 1922, envMul 1958, ampOf 1959, Voice 1962
- **voices** (line 2077): polyOn 2079, polyOff 2084, mono 2085, playRec 2091, playPhrase 2095, releaseAll 2098, lineAt 2161, setHostScale 2162
- **script starts** (line 2166): (no functions)
- **ENGINE** (line 2192): isMan 2218, kickOn 2219, kickHeld 2220, rnd 2393, euclid 2398, charOf 2403, genSteps 2404, varWeight 2431, mutateSteps 2432, mutateStepsX 2433, variant 2467, anySolo 2472, fillOn 2474, condOk 2476, dlgPalette 2491, dlgPlan 2493, lifeInfo 2517, eventsAt 2524, stepDur 2555, grooveOff 2559, hitsOf 2569, midiNote 2574, mname 2582, inScale 2583, snap 2584, nearestPC 2585
- **STATE** (line 2588): panMig 2594, freshLane 2598, lanesFrom 2605, oOpen 2615, migrateFx 2619, migrateSnap 2622, invalidate 2641, polyLen 2644, regen 2654, regenAll 2659, applyPreset 2660, varyLane 2678, metric 2694, contextOcc 2695, randLane 2702, hasHits 2739, anchorIds 2743, lhlW 2745, syncOf 2747, patternFeatures 2754, sugTargets 2769, scorePattern 2776, hamming 2786, currentPat 2787, makeSuggestions 2788, applySuggestion 2806, hSnap 2814, hApply 2815, hRecord 2816, hStep 2821, favSnap 2823, favLoad 2825, resetBasis 2832, tuneToKey 2838, resetKit 2840, rollKit 2841, rollLane 2846, patternData 2857, kitData 2858, applyPattern 2859, applyKit 2867
- **AUDIO** (line 2879): noiseBuf 2895, env 2896, noise 2897, mtof 2898, bq 2899, tone 2900, cents 2908, vMem 2910, vBell 2942, pulseBuf 2972, vUdu 2978, vTri 2995, vTabla 3014, vBayan 3031, vWood 3041, vTamb 3053, vClap 3073, vShk 3084, driftAt 3095, chokeIn 3103, voice 3107, voiceKind 3119, vcSpec 3141, vcGet 3148, vcPump 3151
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3161): irKey 3172, makeIR 3173, springIR 3200, unityCurve 3212, satCurve 3213, buildReverb 3214, bloomOn 3226, bloomHz 3227, bloomSync 3228, bloomStep 3231, buildDelay 3232, tapeCurve 3261, NgomaFilterCore 3265, NgomaFilterProc 3333, NgomaRecProc 3346, NgomaCombProc 3354, NgomaShimProc 3368, NgomaPlaitsProc 3379, loadFilter 3406, attachFilter 3414, smooth 3433, mgDecK 3435, mgP 3436, buildMagic 3437, presetTrim 3473, magicSync 3474, magicWorklet 3486, combFallback 3492, resChord 3502, resMsg 3511, resStep 3513, resHz 3515, procSync 3516, combStep 3528, formantStep 3534, glitchStep 3539, cosmosErase 3553, padNotes 3563, padRoot 3572, padLoops 3573, softTone 3582, padSc 3595, padNt 3596, chProgOf 3606, chOn 3607, chPer 3608, chSemi 3609, chDegOf 3610, chWander 3612, chordAt 3617, chName 3619, chKey 3621, chTn 3626, chLabel 3632, tideState 3638, padTides 3650, tideTone 3655, echoPhrase 3664, padEchoes 3670, echoTone 3677, seasonChord 3688, seasonHold 3701, padSeasons 3702, warmVoice 3711, subVoice 3718, grain 3721, padRare 3727, buildPad 3735, padCutHz 3750, unitFlt 3754, fltHz 3755, fltFmt 3756, unitWet 3757, unitEcho 3758, unitTr 3759, trDeg 3760, pmtof 3761, wTry 3764, padTy 3765, padLive 3766, padSync 3767, padDrone 3780, droneVoice 3782, worpSeed 3792, padRecOn 3797, stepNow 3798, nrecUI 3799, nrecClicks 3807, nrecToggle 3810, nrecStop 3817, nrecNote 3818, nrecTick 3821, padMine 3827, worpSpec 3828, worpCode 3829, worpFlt 3831, worpToken 3832
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3833): lineMine 3845, recOn 3846, midiConnect 3847, midiPadOK 3854, midiDest 3855, midiShort 3856, midiUI 3857, midiQT 3862, midiKey 3865, ngMidi 3867, midiAuto 3873, leadAnchorTpl 3875, leadAnchorFn 3878, leadLv 3884, leadDrum 3885, plOn 3895, plPatch 3896, plMove 3902, plBytes 3907, plEngine 3908, plSync 3911, plNote 3913, plKeys 3915, plPhrase 3917, plSemi 3918, plRec 3920, plBar 3922, leadGain 3929, leadMeasure 3930, buildDub 3940, dubSync 3945, fltQ 3949, buildLead 3950
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3956): fldTrim 3971, fldId 3972, fldInfo 3973, fldKey 3974, fldBuf 3975, fldNorm 3976, fldDecode 3978, fldLoad 3979, fldOwnLoad 3988, fldOwnSet 3990, buildField 3991, fldLive 3995, fldHz 3996, fldStopLoop 3997, fldSync 3998, fldWalk 4005, fldStep 4006, fldDuck 4018, fldUI 4019, leadLive 4023, leadSpec 4024, leadSync 4025, leadEngine 4027, leadBar 4037, lcdSet 4046, leadUI 4047, worpBar 4052, worpUI 4068, worpParse 4074, worpUse 4080, worpHash 4082, WBC 4085, ctxEpoch 4086, worpState 4088, worpPost 4091, worpMsg 4096, worpPanel 4121, padBar 4127, buildGraph 4153, buildRoom 4183, roomSync 4188, clipCurve 4190, vetOn 4192, vetAmt 4193, VET_TRIM 4194, masterCurve 4198, buildVet 4199, vetSync 4213, shaperCurve 4217, lfoHz 4219, lfoPeriod 4220, cutPos 4221, cutHz 4222, syncFx 4223, pv 4253, syncGraph 4254, animCurve 4260, animValues 4262, applyAnim 4264, animLive 4270, fxTail 4272, flamGuard 4285, mgQ 4290, scheduleStep 4291, evN 4317, hitGate 4318, AUD 4327, STABLE 4328, loadLate 4329, stableSet 4330, ensureCtx 4333, tick 4334, start 4339, stop 4341, setDrop 4347, setDrumsOff 4350, dropApply 4351, dropMask 4356, preview 4357, $ 4364, mvolGain 4366, setMvol 4367, initMvol 4371, flashLed 4377
- **First visit: invite to press Play, then one next step** (line 4383): onbSave 4386, hintShow 4387, hintHide 4388, onbInit 4389, onbPlayed 4391, onbActed 4392, setPlayUI 4394, clearNow 4395, showDrift 4396, magicGlow 4404
- **Scope: a quiet oscilloscope in the house colours** (line 4411): scopeInit 4415, scopeCalm 4419, scopeCols 4420, scopeHit 4421, scopeWake 4422, scopeGrid 4423, scopeTrace 4426, scopeIdle 4428, scopeFrame 4429, draw 4448, makeSegK 4479, makeSelK 4483, makeKnob 4487, editX 4513, kfoldSeen 4523, kfoldHint 4524, laneRow 4528, paintPending 4608, paintCell 4610, editCell 4626, euRow 4638, renderLanes 4653, renderStyles 4665, initTips 4694, initValues 4709, bindMacro 4710, initControls 4714, status 5058, afterLoad 5059, updHist 5060, renderFavs 5061, inflate 5072, loadShared 5073, fileBase 5078
- **EXPORT: WAV** (line 5083): wavBytes 5085, kCoefs 5097, loudness 5102, truePeak 5112, midiBytes 5118, midiBytesX 5119, chLen 5146, chordMidiBytes 5147, CRC 5154, crc32 5155, zipBlob 5156, loopLen 5176, renderLoop 5178, renderLoopX 5179
- **Capture: keep what you just heard** (line 5188): capAttach 5193, capStart 5201, capLog 5202, capWindow 5203, capAudio 5209, capMidi 5213, capture 5223
- **Delivery: a folder you picked (no zip), or a zip download** (line 5236): idb 5238, kvSet 5239, kvGet 5240, outUI 5241, outPick 5242, outReady 5243, writeFiles 5244, deliver 5246, resampleTo 5252
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5254): dwKey 5256, dwPrepare 5257
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5262): jamTrack 5269, jamPut 5270, jamRec 5272, jamStart 5274, jamWorp 5283, jamUI 5286, jamStop 5290, jamWav 5300, jamFiles 5305
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5312): bbUI 5316, bbPick 5317, bbName 5318, bbSend 5322, exportLoop 5342
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5383): m4lAlign 5386, m4lInit 5390
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5422): onBar 5426, qRun 5430, qMark 5432, qDraw 5435
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5440): scenesRender 5442, sceneStore 5453, sceneClear 5454, sceneRecall 5455
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5458): morphCap 5467, morphStart 5469, morphSet 5478, morphInd 5495, morphSnap 5497, scBase 5501, scEdited 5502, morphStep 5505, morphEnd 5507, morphUI 5515, setView 5527
- **script starts** (line 5540): (no functions)

## Worp: public/worp/index.html (1898 lines)

- **script starts** (line 445): $ 447, mtof 458, mod 459
- **seeded dice** (line 461): rng 462, scaleLabel 473, semis 474
- **patch generation: chance inside musical limits** (line 476): genSpectrum 477, fromHist 491, histEntry 492, genName 493, uniqueName 502, genPatch 503
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 626): anchorFrom 644, euclidW 646, genPhraseStyle 647, rnd01 686, phraseAt 689, phraseAt0 691, phCx 699, phZ 700, phraseCore 701, phraseDesc 736, lvSd 745, lvMem 746, lvP2 751, lvCt 752, lvSnap 753, lvBar 754, phraseV2 770, phraseOut 778
- **the modular part: sources, cables, re-patching** (line 780): genMods 783, genFx 835, fxDesc 863, destRange 872, destName 884, srcDesc 885
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 894): NgomaFilterCore 897, NgomaFilterProc 965, WorpRecProc 976, cutHz 990, loadFilter 991, syncFilter 998, saveFilter 1002, saveEnv 1005
- **audio graph** (line 1007): makeIR 1009, curve 1022, initAudio 1023, gateStep 1060, prepWaves 1062, applyFx 1069, mixVal 1091, applyMix 1092, loopD 1094, airNorm 1095, foldCurve 1096, bitCurve 1099, quantCurve 1100, chroma 1101, fxRotor 1108, fxBitplane 1116, fxHalo 1123, fxStrings 1141, fxShifter 1149, fxSonar 1163, buildFx 1173, retireFx 1181, globalParams 1185, buildMods 1186, retireMods 1207, modTick 1213, envMul 1249, ampOf 1250, Voice 1253
- **voices** (line 1368): polyOn 1370, polyOff 1375, mono 1376, playRec 1382, playPhrase 1386, releaseAll 1389, liveOn 1395, liveOff 1405, setSustain 1418
- **state** (line 1420): cur 1422, getBpm 1423, newSeed 1424, load 1425, save 1426, setPatch 1428, roll 1443, back 1448, setMode 1452
- **playing by itself** (line 1466): startDrone 1468, evolveDrone 1469, tick 1477, startPlay 1488, stopPlay 1499
- **MIDI** (line 1506): midiStatus 1508, initMIDI 1509, onMidi 1517, renderLearn 1534
- **rendering** (line 1541): noteName 1542, layerDetail 1543, layerTag 1550
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1552): BC 1557, ngomaOpen 1558, linked 1563, outGain 1565, epochToCtx 1566, hostT0 1569, relock 1570, transportSync 1572, worpPost 1580, setPlayUI 1581, hostVoicing 1586, applyHost 1588, hostChanged 1590, renderFollow 1597, focusNgoma 1600, toNgoma 1604, onHostMsg 1605, recStart 1622, recStop 1626, patchCode 1631, fltTok 1634, shareToken 1635, setFLT 1636, setENV 1637, envTok 1638, envNeutral 1639, hearInNgoma 1645, renderLive 1648, parseToken 1651, render 1655, renderFx 1681, renderPatch 1687, renderMusic 1696, lineHas 1713, lineUI 1714, lineSet 1716, drawSteps 1720, recLine 1729, recQ 1737, recFinish 1738, kbStart 1748, buildKb 1749, markKey 1757, ptrUp 1761, togglePlay 1776
- **ring visual** (line 1786): ringAn 1790, draw 1791
- **wiring** (line 1815): renderFilter 1835, secT 1844, renderEnv 1845, fillRange 1891
