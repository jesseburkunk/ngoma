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

## Ngoma: public/index.html (5533 lines)

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
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1438): anchorFrom 1456, euclidW 1458, genPhraseStyle 1459, rnd01 1498, phraseAt 1501, phraseAt0 1503, phCx 1511, phZ 1512, phraseCore 1513, phraseDesc 1548, lvSd 1557, lvMem 1558, lvP2 1563, lvCt 1564, lvSnap 1565, lvBar 1566, phraseV2 1582, phraseOut 1590
- **the modular part: sources, cables, re-patching** (line 1592): genMods 1595, genFx 1647, fxDesc 1675, destRange 1684, destName 1696, srcDesc 1697, create 1707, makeIR 1714, curve 1727, initGraph 1728, gateStep 1759, prepWaves 1761, applyFx 1768, mixVal 1790, applyMix 1791, loopD 1793, airNorm 1794, foldCurve 1795, bitCurve 1798, quantCurve 1799, chroma 1800, fxRotor 1807, fxBitplane 1815, fxHalo 1822, fxStrings 1840, fxShifter 1848, fxSonar 1862, buildFx 1872, retireFx 1880, globalParams 1884, buildMods 1885, retireMods 1906, modTick 1912, envMul 1948, ampOf 1949, Voice 1952
- **voices** (line 2067): polyOn 2069, polyOff 2074, mono 2075, playRec 2081, playPhrase 2085, releaseAll 2088, lineAt 2151, setHostScale 2152
- **script starts** (line 2156): (no functions)
- **ENGINE** (line 2182): isMan 2208, kickOn 2209, kickHeld 2210, rnd 2383, euclid 2388, charOf 2393, genSteps 2394, varWeight 2421, mutateSteps 2422, mutateStepsX 2423, variant 2457, anySolo 2462, fillOn 2464, condOk 2466, dlgPalette 2481, dlgPlan 2483, lifeInfo 2507, eventsAt 2514, stepDur 2545, grooveOff 2549, hitsOf 2559, midiNote 2564, mname 2572, inScale 2573, snap 2574, nearestPC 2575
- **STATE** (line 2578): panMig 2584, freshLane 2588, lanesFrom 2595, oOpen 2605, migrateFx 2609, migrateSnap 2612, invalidate 2631, polyLen 2634, regen 2644, regenAll 2649, applyPreset 2650, varyLane 2668, metric 2684, contextOcc 2685, randLane 2692, hasHits 2729, anchorIds 2733, lhlW 2735, syncOf 2737, patternFeatures 2744, sugTargets 2759, scorePattern 2766, hamming 2776, currentPat 2777, makeSuggestions 2778, applySuggestion 2796, hSnap 2804, hApply 2805, hRecord 2806, hStep 2811, favSnap 2813, favLoad 2815, resetBasis 2822, tuneToKey 2828, resetKit 2830, rollKit 2831, rollLane 2836, patternData 2847, kitData 2848, applyPattern 2849, applyKit 2857
- **AUDIO** (line 2869): noiseBuf 2885, env 2886, noise 2887, mtof 2888, bq 2889, tone 2890, cents 2898, vMem 2900, vBell 2932, pulseBuf 2962, vUdu 2968, vTri 2985, vTabla 3004, vBayan 3021, vWood 3031, vTamb 3043, vClap 3063, vShk 3074, driftAt 3085, chokeIn 3093, voice 3097, voiceKind 3109, vcSpec 3131, vcGet 3138, vcPump 3141
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3151): irKey 3162, makeIR 3163, springIR 3190, unityCurve 3202, satCurve 3203, buildReverb 3204, bloomOn 3216, bloomHz 3217, bloomSync 3218, bloomStep 3221, buildDelay 3222, tapeCurve 3251, NgomaFilterCore 3255, NgomaFilterProc 3323, NgomaRecProc 3336, NgomaCombProc 3344, NgomaShimProc 3358, NgomaPlaitsProc 3369, loadFilter 3396, attachFilter 3404, smooth 3423, mgDecK 3425, mgP 3426, buildMagic 3427, presetTrim 3463, magicSync 3464, magicWorklet 3476, combFallback 3482, resChord 3492, resMsg 3501, resStep 3503, resHz 3505, procSync 3506, combStep 3518, formantStep 3524, glitchStep 3529, cosmosErase 3543, padNotes 3553, padRoot 3562, padLoops 3563, softTone 3572, padSc 3585, padNt 3586, chProgOf 3596, chOn 3597, chPer 3598, chSemi 3599, chDegOf 3600, chWander 3602, chordAt 3607, chName 3609, chKey 3611, chTn 3616, chLabel 3622, tideState 3628, padTides 3640, tideTone 3645, echoPhrase 3654, padEchoes 3660, echoTone 3667, seasonChord 3678, seasonHold 3691, padSeasons 3692, warmVoice 3701, subVoice 3708, grain 3711, padRare 3717, buildPad 3725, padCutHz 3740, unitFlt 3744, fltHz 3745, fltFmt 3746, unitWet 3747, unitEcho 3748, unitTr 3749, trDeg 3750, pmtof 3751, wTry 3754, padTy 3755, padLive 3756, padSync 3757, padDrone 3770, droneVoice 3772, worpSeed 3782, padRecOn 3787, stepNow 3788, nrecUI 3789, nrecClicks 3797, nrecToggle 3800, nrecStop 3807, nrecNote 3808, nrecTick 3811, padMine 3817, worpSpec 3818, worpCode 3819, worpFlt 3821, worpToken 3822
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3823): lineMine 3835, recOn 3836, midiConnect 3837, midiPadOK 3844, midiDest 3845, midiShort 3846, midiUI 3847, midiQT 3852, midiKey 3855, ngMidi 3857, midiAuto 3863, leadAnchorTpl 3865, leadAnchorFn 3868, leadLv 3874, leadDrum 3875, plOn 3885, plPatch 3886, plMove 3892, plBytes 3897, plEngine 3898, plSync 3901, plNote 3903, plKeys 3905, plPhrase 3907, plSemi 3908, plRec 3910, plBar 3912, leadGain 3919, leadMeasure 3920, buildDub 3930, dubSync 3935, fltQ 3939, buildLead 3940
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3946): fldTrim 3961, fldId 3962, fldInfo 3963, fldKey 3964, fldBuf 3965, fldNorm 3966, fldDecode 3968, fldLoad 3969, fldOwnLoad 3978, fldOwnSet 3980, buildField 3981, fldLive 3985, fldHz 3986, fldStopLoop 3987, fldSync 3988, fldWalk 3995, fldStep 3996, fldDuck 4008, fldUI 4009, leadLive 4013, leadSpec 4014, leadSync 4015, leadEngine 4017, leadBar 4027, lcdSet 4036, leadUI 4037, worpBar 4042, worpUI 4058, worpParse 4064, worpUse 4070, worpHash 4072, WBC 4075, ctxEpoch 4076, worpState 4078, worpPost 4081, worpMsg 4086, worpPanel 4111, padBar 4117, buildGraph 4143, buildRoom 4173, roomSync 4178, clipCurve 4180, vetOn 4182, vetAmt 4183, VET_TRIM 4184, masterCurve 4188, buildVet 4189, vetSync 4203, shaperCurve 4207, lfoHz 4209, lfoPeriod 4210, cutPos 4211, cutHz 4212, syncFx 4213, pv 4243, syncGraph 4244, animCurve 4250, animValues 4252, applyAnim 4254, animLive 4260, fxTail 4262, flamGuard 4275, mgQ 4280, scheduleStep 4281, evN 4307, hitGate 4308, AUD 4317, STABLE 4318, loadLate 4319, stableSet 4320, ensureCtx 4323, tick 4324, start 4329, stop 4331, setDrop 4337, setDrumsOff 4340, dropApply 4341, dropMask 4346, preview 4347, $ 4354, mvolGain 4356, setMvol 4357, initMvol 4361, flashLed 4367
- **First visit: invite to press Play, then one next step** (line 4373): onbSave 4376, hintShow 4377, hintHide 4378, onbInit 4379, onbPlayed 4381, onbActed 4382, setPlayUI 4384, clearNow 4385, showDrift 4386, magicGlow 4394
- **Scope: a quiet oscilloscope in the house colours** (line 4401): scopeInit 4405, scopeCalm 4409, scopeCols 4410, scopeHit 4411, scopeWake 4412, scopeGrid 4413, scopeTrace 4416, scopeIdle 4418, scopeFrame 4419, draw 4438, makeSegK 4469, makeSelK 4473, makeKnob 4477, editX 4503, kfoldSeen 4513, kfoldHint 4514, laneRow 4518, paintPending 4598, paintCell 4600, editCell 4616, euRow 4628, renderLanes 4643, renderStyles 4655, initTips 4684, initValues 4699, bindMacro 4700, initControls 4704, status 5048, afterLoad 5049, updHist 5050, renderFavs 5051, inflate 5062, loadShared 5063, fileBase 5068
- **EXPORT: WAV** (line 5073): wavBytes 5075, kCoefs 5087, loudness 5092, truePeak 5102, midiBytes 5108, midiBytesX 5109, chLen 5136, chordMidiBytes 5137, CRC 5144, crc32 5145, zipBlob 5146, loopLen 5166, renderLoop 5168, renderLoopX 5169
- **Capture: keep what you just heard** (line 5178): capAttach 5183, capStart 5191, capLog 5192, capWindow 5193, capAudio 5199, capMidi 5203, capture 5213
- **Delivery: a folder you picked (no zip), or a zip download** (line 5226): idb 5228, kvSet 5229, kvGet 5230, outUI 5231, outPick 5232, outReady 5233, writeFiles 5234, deliver 5236, resampleTo 5242
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5244): dwKey 5246, dwPrepare 5247
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5252): jamTrack 5259, jamPut 5260, jamRec 5262, jamStart 5264, jamWorp 5273, jamUI 5276, jamStop 5280, jamWav 5290, jamFiles 5295
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5302): bbUI 5306, bbPick 5307, bbName 5308, bbSend 5312, exportLoop 5332
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5373): m4lAlign 5376, m4lInit 5380
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5412): onBar 5416, qRun 5420, qMark 5422, qDraw 5425
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5430): scenesRender 5432, sceneStore 5443, sceneClear 5444, sceneRecall 5445
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5448): morphCap 5457, morphStart 5459, morphSet 5468, morphInd 5485, morphSnap 5487, scBase 5491, scEdited 5492, morphStep 5495, morphEnd 5497, morphUI 5505, setView 5517
- **script starts** (line 5530): (no functions)

## Worp: public/worp/index.html (1888 lines)

- **script starts** (line 445): $ 447, mtof 458, mod 459
- **seeded dice** (line 461): rng 462, scaleLabel 473, semis 474
- **patch generation: chance inside musical limits** (line 476): genSpectrum 477, fromHist 491, histEntry 492, genName 493, uniqueName 502, genPatch 503
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 616): anchorFrom 634, euclidW 636, genPhraseStyle 637, rnd01 676, phraseAt 679, phraseAt0 681, phCx 689, phZ 690, phraseCore 691, phraseDesc 726, lvSd 735, lvMem 736, lvP2 741, lvCt 742, lvSnap 743, lvBar 744, phraseV2 760, phraseOut 768
- **the modular part: sources, cables, re-patching** (line 770): genMods 773, genFx 825, fxDesc 853, destRange 862, destName 874, srcDesc 875
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 884): NgomaFilterCore 887, NgomaFilterProc 955, WorpRecProc 966, cutHz 980, loadFilter 981, syncFilter 988, saveFilter 992, saveEnv 995
- **audio graph** (line 997): makeIR 999, curve 1012, initAudio 1013, gateStep 1050, prepWaves 1052, applyFx 1059, mixVal 1081, applyMix 1082, loopD 1084, airNorm 1085, foldCurve 1086, bitCurve 1089, quantCurve 1090, chroma 1091, fxRotor 1098, fxBitplane 1106, fxHalo 1113, fxStrings 1131, fxShifter 1139, fxSonar 1153, buildFx 1163, retireFx 1171, globalParams 1175, buildMods 1176, retireMods 1197, modTick 1203, envMul 1239, ampOf 1240, Voice 1243
- **voices** (line 1358): polyOn 1360, polyOff 1365, mono 1366, playRec 1372, playPhrase 1376, releaseAll 1379, liveOn 1385, liveOff 1395, setSustain 1408
- **state** (line 1410): cur 1412, getBpm 1413, newSeed 1414, load 1415, save 1416, setPatch 1418, roll 1433, back 1438, setMode 1442
- **playing by itself** (line 1456): startDrone 1458, evolveDrone 1459, tick 1467, startPlay 1478, stopPlay 1489
- **MIDI** (line 1496): midiStatus 1498, initMIDI 1499, onMidi 1507, renderLearn 1524
- **rendering** (line 1531): noteName 1532, layerDetail 1533, layerTag 1540
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1542): BC 1547, ngomaOpen 1548, linked 1553, outGain 1555, epochToCtx 1556, hostT0 1559, relock 1560, transportSync 1562, worpPost 1570, setPlayUI 1571, hostVoicing 1576, applyHost 1578, hostChanged 1580, renderFollow 1587, focusNgoma 1590, toNgoma 1594, onHostMsg 1595, recStart 1612, recStop 1616, patchCode 1621, fltTok 1624, shareToken 1625, setFLT 1626, setENV 1627, envTok 1628, envNeutral 1629, hearInNgoma 1635, renderLive 1638, parseToken 1641, render 1645, renderFx 1671, renderPatch 1677, renderMusic 1686, lineHas 1703, lineUI 1704, lineSet 1706, drawSteps 1710, recLine 1719, recQ 1727, recFinish 1728, kbStart 1738, buildKb 1739, markKey 1747, ptrUp 1751, togglePlay 1766
- **ring visual** (line 1776): ringAn 1780, draw 1781
- **wiring** (line 1805): renderFilter 1825, secT 1834, renderEnv 1835, fillRange 1881
