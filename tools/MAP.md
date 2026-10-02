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

## Ngoma: public/index.html (5506 lines)

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
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3823): lineMine 3835, recOn 3836, midiConnect 3837, midiPadOK 3844, midiDest 3845, midiShort 3846, midiUI 3847, midiQT 3852, midiKey 3855, ngMidi 3857, midiAuto 3863, leadAnchorTpl 3865, leadAnchorFn 3868, leadLv 3874, leadDrum 3875, plOn 3883, plPatch 3884, plBytes 3887, plEngine 3888, plSync 3891, plNote 3893, plKeys 3895, plPhrase 3897, plSemi 3898, plRec 3900, plBar 3902, leadGain 3908, leadMeasure 3909, buildDub 3919, dubSync 3924, fltQ 3928, buildLead 3929
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3935): fldTrim 3950, fldId 3951, fldInfo 3952, fldKey 3953, fldBuf 3954, fldNorm 3955, fldDecode 3957, fldLoad 3958, fldOwnLoad 3967, fldOwnSet 3969, buildField 3970, fldLive 3974, fldHz 3975, fldStopLoop 3976, fldSync 3977, fldWalk 3984, fldStep 3985, fldDuck 3997, fldUI 3998, leadLive 4002, leadSpec 4003, leadSync 4004, leadEngine 4006, leadBar 4016, lcdSet 4025, leadUI 4026, worpBar 4031, worpUI 4047, worpParse 4053, worpUse 4059, worpHash 4061, WBC 4064, ctxEpoch 4065, worpState 4067, worpPost 4070, worpMsg 4075, worpPanel 4100, padBar 4106, buildGraph 4132, buildRoom 4162, roomSync 4167, clipCurve 4169, vetOn 4171, vetAmt 4172, VET_TRIM 4173, masterCurve 4177, buildVet 4178, vetSync 4192, shaperCurve 4196, lfoHz 4198, lfoPeriod 4199, cutPos 4200, cutHz 4201, syncFx 4202, pv 4232, syncGraph 4233, animCurve 4239, animValues 4241, applyAnim 4243, animLive 4249, fxTail 4251, flamGuard 4264, mgQ 4269, scheduleStep 4270, evN 4296, hitGate 4297, AUD 4306, STABLE 4307, loadLate 4308, stableSet 4309, ensureCtx 4312, tick 4313, start 4318, stop 4320, setDrop 4326, setDrumsOff 4329, dropApply 4330, dropMask 4335, preview 4336, $ 4343, mvolGain 4345, setMvol 4346, initMvol 4350, flashLed 4356
- **First visit: invite to press Play, then one next step** (line 4362): onbSave 4365, hintShow 4366, hintHide 4367, onbInit 4368, onbPlayed 4370, onbActed 4371, setPlayUI 4373, clearNow 4374, showDrift 4375, magicGlow 4383
- **Scope: a quiet oscilloscope in the house colours** (line 4390): scopeInit 4394, scopeCalm 4398, scopeCols 4399, scopeHit 4400, scopeWake 4401, scopeGrid 4402, scopeTrace 4405, scopeIdle 4407, scopeFrame 4408, draw 4427, makeSegK 4458, makeSelK 4462, makeKnob 4466, editX 4492, kfoldSeen 4502, kfoldHint 4503, laneRow 4507, paintPending 4587, paintCell 4589, editCell 4605, euRow 4617, renderLanes 4632, renderStyles 4644, initTips 4673, initValues 4688, bindMacro 4689, initControls 4693, status 5021, afterLoad 5022, updHist 5023, renderFavs 5024, inflate 5035, loadShared 5036, fileBase 5041
- **EXPORT: WAV** (line 5046): wavBytes 5048, kCoefs 5060, loudness 5065, truePeak 5075, midiBytes 5081, midiBytesX 5082, chLen 5109, chordMidiBytes 5110, CRC 5117, crc32 5118, zipBlob 5119, loopLen 5139, renderLoop 5141, renderLoopX 5142
- **Capture: keep what you just heard** (line 5151): capAttach 5156, capStart 5164, capLog 5165, capWindow 5166, capAudio 5172, capMidi 5176, capture 5186
- **Delivery: a folder you picked (no zip), or a zip download** (line 5199): idb 5201, kvSet 5202, kvGet 5203, outUI 5204, outPick 5205, outReady 5206, writeFiles 5207, deliver 5209, resampleTo 5215
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5217): dwKey 5219, dwPrepare 5220
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5225): jamTrack 5232, jamPut 5233, jamRec 5235, jamStart 5237, jamWorp 5246, jamUI 5249, jamStop 5253, jamWav 5263, jamFiles 5268
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5275): bbUI 5279, bbPick 5280, bbName 5281, bbSend 5285, exportLoop 5305
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5346): m4lAlign 5349, m4lInit 5353
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5385): onBar 5389, qRun 5393, qMark 5395, qDraw 5398
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5403): scenesRender 5405, sceneStore 5416, sceneClear 5417, sceneRecall 5418
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5421): morphCap 5430, morphStart 5432, morphSet 5441, morphInd 5458, morphSnap 5460, scBase 5464, scEdited 5465, morphStep 5468, morphEnd 5470, morphUI 5478, setView 5490
- **script starts** (line 5503): (no functions)

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
