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

## Ngoma: public/index.html (5627 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1313): mtof 1328, mod 1329
- **seeded dice** (line 1331): rng 1332, scaleLabel 1343, semis 1344
- **patch generation: chance inside musical limits** (line 1346): genSpectrum 1347, fromHist 1361, histEntry 1362, genName 1363, uniqueName 1372, genPatch 1373
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1496): anchorFrom 1514, euclidW 1516, genPhraseStyle 1517, rnd01 1556, phraseAt 1559, phraseAt0 1561, phCx 1569, phZ 1570, phraseCore 1571, phraseDesc 1606, lvSd 1615, lvMem 1616, lvP2 1621, lvCt 1622, lvSnap 1623, lvBar 1624, phraseV2 1640, phraseOut 1648
- **the modular part: sources, cables, re-patching** (line 1650): genMods 1653, genFx 1705, fxDesc 1733, destRange 1742, destName 1754, srcDesc 1755, create 1765, makeIR 1772, curve 1785, initGraph 1786, gateStep 1817, prepWaves 1819, applyFx 1826, mixVal 1848, applyMix 1849, loopD 1851, airNorm 1852, foldCurve 1853, bitCurve 1856, quantCurve 1857, chroma 1858, fxRotor 1865, fxBitplane 1873, fxHalo 1880, fxStrings 1898, fxShifter 1906, fxSonar 1920, buildFx 1930, retireFx 1938, globalParams 1942, buildMods 1943, retireMods 1964, modTick 1970, envMul 2006, ampOf 2007, Voice 2010
- **voices** (line 2125): polyOn 2127, polyOff 2132, mono 2133, playRec 2139, playPhrase 2143, releaseAll 2146, lineAt 2209, setHostScale 2210
- **script starts** (line 2214): (no functions)
- **ENGINE** (line 2240): isMan 2266, kickOn 2267, kickHeld 2268, rnd 2441, euclid 2446, charOf 2451, genSteps 2452, varWeight 2479, mutateSteps 2480, mutateStepsX 2481, variant 2515, anySolo 2520, fillOn 2522, condOk 2524, dlgPalette 2539, dlgPlan 2541, lifeInfo 2565, eventsAt 2572, stepDur 2603, grooveOff 2607, hitsOf 2617, midiNote 2622, mname 2630, inScale 2631, snap 2632, nearestPC 2633
- **STATE** (line 2636): panMig 2642, freshLane 2646, lanesFrom 2653, oOpen 2663, migrateFx 2667, migrateSnap 2670, invalidate 2689, polyLen 2692, regen 2702, regenAll 2707, applyPreset 2708, varyLane 2726, metric 2742, contextOcc 2743, randLane 2750, hasHits 2787, anchorIds 2791, lhlW 2793, syncOf 2795, patternFeatures 2802, sugTargets 2817, scorePattern 2824, hamming 2834, currentPat 2835, makeSuggestions 2836, applySuggestion 2854, hSnap 2862, hApply 2863, hRecord 2864, hStep 2869, favSnap 2871, favLoad 2873, resetBasis 2880, tuneToKey 2886, resetKit 2888, rollKit 2889, rollLane 2894, patternData 2905, kitData 2906, applyPattern 2907, applyKit 2915
- **AUDIO** (line 2927): noiseBuf 2943, env 2944, noise 2945, mtof 2946, bq 2947, tone 2948, cents 2956, vMem 2958, vBell 2990, pulseBuf 3020, vUdu 3026, vTri 3043, vTabla 3062, vBayan 3079, vWood 3089, vTamb 3101, vClap 3121, vShk 3132, driftAt 3143, chokeIn 3151, voice 3155, voiceKind 3167, vcSpec 3189, vcGet 3196, vcPump 3199
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3209): irKey 3220, makeIR 3221, springIR 3248, unityCurve 3260, satCurve 3261, buildReverb 3262, bloomOn 3274, bloomHz 3275, bloomSync 3276, bloomStep 3279, buildDelay 3280, tapeCurve 3309, NgomaFilterCore 3313, NgomaFilterProc 3381, NgomaRecProc 3394, NgomaCombProc 3402, NgomaShimProc 3416, NgomaPlaitsProc 3427, loadFilter 3454, attachFilter 3462, smooth 3481, mgDecK 3483, mgP 3484, buildMagic 3485, presetTrim 3521, magicSync 3522, magicWorklet 3534, combFallback 3540, resChord 3550, resMsg 3559, resStep 3561, resHz 3563, procSync 3564, combStep 3576, formantStep 3582, glitchStep 3587, cosmosErase 3601, padNotes 3611, padRoot 3620, padLoops 3621, softTone 3630, padSc 3643, padNt 3644, chProgOf 3654, chOn 3655, chPer 3656, chSemi 3657, chDegOf 3658, chWander 3660, chordAt 3665, chName 3667, chKey 3669, chTn 3674, chLabel 3680, tideState 3686, padTides 3698, tideTone 3703, echoPhrase 3712, padEchoes 3718, echoTone 3725, seasonChord 3736, seasonHold 3749, padSeasons 3750, warmVoice 3759, subVoice 3766, grain 3769, padRare 3775, buildPad 3783, padCutHz 3798, unitFlt 3802, fltHz 3803, fltFmt 3804, unitWet 3805, unitEcho 3806, unitTr 3807, trDeg 3808, pmtof 3809, wTry 3812, padTy 3813, padLive 3814, padSync 3815, padDrone 3828, droneVoice 3830, worpSeed 3840, padRecOn 3845, stepNow 3846, nrecUI 3847, nrecClicks 3855, nrecToggle 3858, nrecStop 3865, nrecNote 3866, nrecTick 3869, padMine 3875, worpSpec 3876, worpCode 3877, worpFlt 3879, worpToken 3880
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3881): lineMine 3893, recOn 3894, midiConnect 3895, midiPadOK 3902, midiDest 3903, midiShort 3904, midiUI 3905, midiQT 3910, midiKey 3913, ngMidi 3915, midiAuto 3921, leadAnchorTpl 3923, leadAnchorFn 3926, leadLv 3932, leadDrum 3933, plPatch 3943, plMove 3949, plBytes 3954, plEngine 3955, plSync 3958, plNote 3960, plKeys 3962, plPhrase 3965, plSemi 3966, plRec 3968, plBar 3970, leadGain 3976, buildDub 3980, dubSync 3985, fltQ 3989, buildLead 3990
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3996): fldTrim 4011, fldId 4012, fldInfo 4013, fldKey 4014, fldBuf 4015, fldNorm 4016, fldDecode 4018, fldLoad 4019, fldOwnLoad 4028, fldOwnSet 4030, buildField 4031, fldLive 4035, fldHz 4036, fldStopLoop 4037, fldSync 4038, fldWalk 4045, fldStep 4046, fldDuck 4058, fldUI 4059
- **Candy (v180; Jesse: ear candy instead of a big texture: small sounds without a key that ma** (line 4063): buildCandy 4068, cdLive 4069, cdSeed 4070, cdSrc 4071, cdFid 4072, cdBuf 4073, cdSync 4074, cdPalette 4078, cdHit 4083, cdStep 4092, cdUI 4099, leadLive 4101, leadSpec 4102, leadSync 4103, leadBar 4105, lcdSet 4108, leadUI 4109, worpBar 4113, worpUI 4129, worpParse 4135, worpUse 4141, worpHash 4143, WBC 4146, ctxEpoch 4147, worpState 4149, worpPost 4152, worpMsg 4157, worpPanel 4176, padBar 4182, buildGraph 4208, buildRoom 4238, roomSync 4243, clipCurve 4245, vetOn 4247, vetAmt 4248, VET_TRIM 4249, masterCurve 4253, buildVet 4254, vetSync 4268, shaperCurve 4272, lfoHz 4274, lfoPeriod 4275, cutPos 4276, cutHz 4277, syncFx 4278, pv 4308, syncGraph 4309, animCurve 4315, animValues 4317, applyAnim 4319, animLive 4325, fxTail 4327, flamGuard 4340, mgQ 4345, scheduleStep 4346, evN 4372, hitGate 4373, AUD 4382, STABLE 4383, loadLate 4384, stableSet 4385, ensureCtx 4388, tick 4389, start 4394, stop 4396, setDrop 4401, setDrumsOff 4404, dropApply 4405, dropMask 4410, preview 4411, $ 4418, mvolGain 4420, setMvol 4421, initMvol 4425, flashLed 4431
- **First visit: invite to press Play, then one next step** (line 4437): onbSave 4440, hintShow 4441, hintHide 4442, onbInit 4443, onbPlayed 4445, onbActed 4446, setPlayUI 4448, clearNow 4449, showDrift 4450, magicGlow 4458
- **Scope: a quiet oscilloscope in the house colours** (line 4465): scopeInit 4469, scopeCalm 4473, scopeCols 4474, scopeHit 4475, scopeWake 4476, scopeGrid 4477, scopeTrace 4480, scopeIdle 4482, scopeFrame 4483, draw 4502, makeSegK 4533, makeSelK 4537, makeKnob 4541, editX 4567, kfoldSeen 4577, kfoldHint 4578, laneRow 4582, paintPending 4662, paintCell 4664, editCell 4680, euRow 4692, renderLanes 4707, renderStyles 4719, initTips 4748, initValues 4763, bindMacro 4764, layersLayout 4771, initControls 4791, status 5142, afterLoad 5143, updHist 5144, renderFavs 5145, inflate 5156, loadShared 5157, fileBase 5162
- **EXPORT: WAV** (line 5167): wavBytes 5169, kCoefs 5181, loudness 5186, truePeak 5196, midiBytes 5202, midiBytesX 5203, chLen 5230, chordMidiBytes 5231, CRC 5238, crc32 5239, zipBlob 5240, loopLen 5260, renderLoop 5262, renderLoopX 5263
- **Capture: keep what you just heard** (line 5272): capAttach 5277, capStart 5285, capLog 5286, capWindow 5287, capAudio 5293, capMidi 5297, capture 5307
- **Delivery: a folder you picked (no zip), or a zip download** (line 5320): idb 5322, kvSet 5323, kvGet 5324, outUI 5325, outPick 5326, outReady 5327, writeFiles 5328, deliver 5330, resampleTo 5336
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5338): dwKey 5340, dwPrepare 5341
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5346): jamTrack 5353, jamPut 5354, jamRec 5356, jamStart 5358, jamWorp 5367, jamUI 5370, jamStop 5374, jamWav 5384, jamFiles 5389
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5396): bbUI 5400, bbPick 5401, bbName 5402, bbSend 5406, exportLoop 5426
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5467): m4lAlign 5470, m4lInit 5474
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5506): onBar 5510, qRun 5514, qMark 5516, qDraw 5519
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5524): scenesRender 5526, sceneStore 5537, sceneClear 5538, sceneRecall 5539
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5542): morphCap 5551, morphStart 5553, morphSet 5562, morphInd 5579, morphSnap 5581, scBase 5585, scEdited 5586, morphStep 5589, morphEnd 5591, morphUI 5599, setView 5611
- **script starts** (line 5624): (no functions)

## Worp: public/worp/index.html (1900 lines)

- **script starts** (line 446): $ 448, mtof 459, mod 460
- **seeded dice** (line 462): rng 463, scaleLabel 474, semis 475
- **patch generation: chance inside musical limits** (line 477): genSpectrum 478, fromHist 492, histEntry 493, genName 494, uniqueName 503, genPatch 504
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 627): anchorFrom 645, euclidW 647, genPhraseStyle 648, rnd01 687, phraseAt 690, phraseAt0 692, phCx 700, phZ 701, phraseCore 702, phraseDesc 737, lvSd 746, lvMem 747, lvP2 752, lvCt 753, lvSnap 754, lvBar 755, phraseV2 771, phraseOut 779
- **the modular part: sources, cables, re-patching** (line 781): genMods 784, genFx 836, fxDesc 864, destRange 873, destName 885, srcDesc 886
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 895): NgomaFilterCore 898, NgomaFilterProc 966, WorpRecProc 977, cutHz 991, loadFilter 992, syncFilter 999, saveFilter 1003, saveEnv 1006
- **audio graph** (line 1008): makeIR 1010, curve 1023, initAudio 1024, gateStep 1061, prepWaves 1063, applyFx 1070, mixVal 1092, applyMix 1093, loopD 1095, airNorm 1096, foldCurve 1097, bitCurve 1100, quantCurve 1101, chroma 1102, fxRotor 1109, fxBitplane 1117, fxHalo 1124, fxStrings 1142, fxShifter 1150, fxSonar 1164, buildFx 1174, retireFx 1182, globalParams 1186, buildMods 1187, retireMods 1208, modTick 1214, envMul 1250, ampOf 1251, Voice 1254
- **voices** (line 1369): polyOn 1371, polyOff 1376, mono 1377, playRec 1383, playPhrase 1387, releaseAll 1390, liveOn 1396, liveOff 1406, setSustain 1419
- **state** (line 1421): cur 1423, getBpm 1424, newSeed 1425, load 1426, save 1427, setPatch 1429, roll 1444, back 1449, setMode 1453
- **playing by itself** (line 1468): startDrone 1470, evolveDrone 1471, tick 1479, startPlay 1490, stopPlay 1501
- **MIDI** (line 1508): midiStatus 1510, initMIDI 1511, onMidi 1519, renderLearn 1536
- **rendering** (line 1543): noteName 1544, layerDetail 1545, layerTag 1552
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1554): BC 1559, ngomaOpen 1560, linked 1565, outGain 1567, epochToCtx 1568, hostT0 1571, relock 1572, transportSync 1574, worpPost 1582, setPlayUI 1583, hostVoicing 1588, applyHost 1590, hostChanged 1592, renderFollow 1599, focusNgoma 1602, toNgoma 1606, onHostMsg 1607, recStart 1624, recStop 1628, patchCode 1633, fltTok 1636, shareToken 1637, setFLT 1638, setENV 1639, envTok 1640, envNeutral 1641, hearInNgoma 1647, renderLive 1650, parseToken 1653, render 1657, renderFx 1683, renderPatch 1689, renderMusic 1698, lineHas 1715, lineUI 1716, lineSet 1718, drawSteps 1722, recLine 1731, recQ 1739, recFinish 1740, kbStart 1750, buildKb 1751, markKey 1759, ptrUp 1763, togglePlay 1778
- **ring visual** (line 1788): ringAn 1792, draw 1793
- **wiring** (line 1817): renderFilter 1837, secT 1846, renderEnv 1847, fillRange 1893
