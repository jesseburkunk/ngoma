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

## Ngoma: public/index.html (5647 lines)

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
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1496): anchorFrom 1514, euclidW 1516, genPhraseStyle 1517, rnd01 1556, phraseAt 1559, phraseAt0 1561, phCx 1569, phZ 1570, phraseCore 1571, phraseDesc 1606, lvSd 1615, lvMem 1616, lvP2 1621, lvCt 1622, lvSnap 1623, lvBar 1624, phraseV2 1640, lvMap 1651, phraseOut 1652
- **the modular part: sources, cables, re-patching** (line 1655): genMods 1658, genFx 1710, fxDesc 1738, destRange 1747, destName 1759, srcDesc 1760, create 1770, makeIR 1777, curve 1790, initGraph 1791, gateStep 1822, prepWaves 1824, applyFx 1831, mixVal 1853, applyMix 1854, loopD 1856, airNorm 1857, foldCurve 1858, bitCurve 1861, quantCurve 1862, chroma 1863, fxRotor 1870, fxBitplane 1878, fxHalo 1885, fxStrings 1903, fxShifter 1911, fxSonar 1925, buildFx 1935, retireFx 1943, globalParams 1947, buildMods 1948, retireMods 1969, modTick 1975, envMul 2011, ampOf 2012, Voice 2015
- **voices** (line 2130): polyOn 2132, polyOff 2137, mono 2138, playRec 2144, playPhrase 2148, releaseAll 2151, lineAt 2214, setHostScale 2215
- **script starts** (line 2219): (no functions)
- **ENGINE** (line 2245): isMan 2271, kickOn 2272, kickHeld 2273, rnd 2446, euclid 2451, charOf 2456, genSteps 2457, varWeight 2484, mutateSteps 2485, mutateStepsX 2486, variant 2520, anySolo 2525, fillOn 2527, condOk 2529, dlgPalette 2544, dlgPlan 2546, lifeInfo 2570, eventsAt 2577, stepDur 2608, grooveOff 2612, hitsOf 2622, midiNote 2627, mname 2635, inScale 2636, snap 2637, nearestPC 2638
- **STATE** (line 2641): panMig 2647, freshLane 2651, lanesFrom 2658, oOpen 2668, migrateFx 2672, migrateSnap 2675, invalidate 2694, polyLen 2697, regen 2707, regenAll 2712, applyPreset 2713, varyLane 2731, metric 2747, contextOcc 2748, randLane 2755, hasHits 2792, anchorIds 2796, lhlW 2798, syncOf 2800, patternFeatures 2807, sugTargets 2822, scorePattern 2829, hamming 2839, currentPat 2840, makeSuggestions 2841, applySuggestion 2859, hSnap 2867, hApply 2868, hRecord 2869, hStep 2874, favSnap 2876, favLoad 2878, resetBasis 2885, tuneToKey 2891, resetKit 2893, rollKit 2894, rollLane 2899, patternData 2910, kitData 2911, applyPattern 2912, applyKit 2920
- **AUDIO** (line 2932): noiseBuf 2948, env 2949, noise 2950, mtof 2951, bq 2952, tone 2953, cents 2961, vMem 2963, vBell 2995, pulseBuf 3025, vUdu 3031, vTri 3048, vTabla 3067, vBayan 3084, vWood 3094, vTamb 3106, vClap 3126, vShk 3137, driftAt 3148, chokeIn 3156, voice 3160, voiceKind 3172, vcSpec 3194, vcGet 3201, vcPump 3204
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3214): irKey 3225, makeIR 3226, springIR 3253, unityCurve 3265, satCurve 3266, buildReverb 3267, bloomOn 3279, bloomHz 3280, bloomSync 3281, bloomStep 3284, buildDelay 3285, tapeCurve 3314, NgomaFilterCore 3318, NgomaFilterProc 3386, NgomaRecProc 3399, NgomaCombProc 3407, NgomaShimProc 3421, NgomaPlaitsProc 3432, loadFilter 3459, attachFilter 3467, smooth 3486, mgDecK 3488, mgP 3489, buildMagic 3490, presetTrim 3526, magicSync 3527, magicWorklet 3539, combFallback 3545, resChord 3555, resMsg 3564, resStep 3566, resHz 3568, procSync 3569, combStep 3581, formantStep 3587, glitchStep 3592, cosmosErase 3606, padNotes 3616, padRoot 3625, padLoops 3626, softTone 3635, padSc 3648, padNt 3649, chProgOf 3659, chOn 3660, chPer 3661, chSemi 3662, chDegOf 3663, chWander 3665, chordAt 3670, chName 3672, chKey 3674, chTn 3679, chLabel 3685, tideState 3691, padTides 3703, tideTone 3708, echoPhrase 3717, padEchoes 3723, echoTone 3730, seasonChord 3741, seasonHold 3754, padSeasons 3755, warmVoice 3764, subVoice 3771, grain 3774, padRare 3780, buildPad 3788, padCutHz 3803, unitFlt 3807, fltHz 3808, fltFmt 3809, unitWet 3810, unitEcho 3811, unitTr 3812, trDeg 3813, pmtof 3814, wTry 3817, padTy 3818, padLive 3819, padSync 3820, padDrone 3833, droneVoice 3835, worpSeed 3845, padRecOn 3850, stepNow 3851, nrecUI 3852, nrecClicks 3860, nrecToggle 3863, nrecStop 3870, nrecNote 3871, nrecTick 3874, padMine 3880, worpSpec 3881, worpCode 3882, worpFlt 3884, worpToken 3885
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3886): lineMine 3898, recOn 3899, midiConnect 3900, midiPadOK 3907, midiDest 3908, midiShort 3909, midiUI 3910, midiQT 3915, midiKey 3918, ngMidi 3920, midiAuto 3926, leadAnchorTpl 3928, leadAnchorFn 3931, leadLen 3937, leadLv 3938, leadDrum 3939, plPatch 3949, plHarm 3959, plMove 3961, plBytes 3966, plEngine 3967, plSync 3970, plNote 3972, plKeys 3974, plPhrase 3977, plSemi 3978, plRec 3980, plBar 3982, leadGain 3992, buildDub 3996, dubSync 4001, fltQ 4005, buildLead 4006
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 4012): fldTrim 4027, fldId 4028, fldInfo 4029, fldKey 4030, fldBuf 4031, fldNorm 4032, fldDecode 4034, fldLoad 4035, fldOwnLoad 4044, fldOwnSet 4046, buildField 4047, fldLive 4051, fldHz 4052, fldStopLoop 4053, fldSync 4054, fldWalk 4061, fldStep 4062, fldDuck 4074, fldUI 4075
- **Candy (v180; Jesse: ear candy instead of a big texture: small sounds without a key that ma** (line 4079): buildCandy 4084, cdLive 4085, cdSeed 4086, cdSrc 4087, cdFid 4088, cdBuf 4089, cdSync 4090, cdPalette 4094, cdHit 4099, cdStep 4108, cdUI 4115, leadLive 4117, leadSpec 4118, leadSync 4119, leadBar 4121, lcdSet 4124, leadUI 4125, worpBar 4129, worpUI 4145, worpParse 4151, worpUse 4157, worpHash 4159, WBC 4162, ctxEpoch 4163, worpState 4165, worpPost 4168, worpMsg 4173, worpPanel 4192, padBar 4198, buildGraph 4224, buildRoom 4254, roomSync 4259, clipCurve 4261, vetOn 4263, vetAmt 4264, VET_TRIM 4265, masterCurve 4269, buildVet 4270, vetSync 4284, shaperCurve 4288, lfoHz 4290, lfoPeriod 4291, cutPos 4292, cutHz 4293, syncFx 4294, pv 4324, syncGraph 4325, animCurve 4331, animValues 4333, applyAnim 4335, animLive 4341, fxTail 4343, flamGuard 4356, mgQ 4361, scheduleStep 4362, evN 4388, hitGate 4389, AUD 4398, STABLE 4399, loadLate 4400, stableSet 4401, ensureCtx 4404, tick 4405, start 4410, stop 4412, setDrop 4417, setDrumsOff 4420, dropApply 4421, dropMask 4426, preview 4427, $ 4434, mvolGain 4436, setMvol 4437, initMvol 4441, flashLed 4447
- **First visit: invite to press Play, then one next step** (line 4453): onbSave 4456, hintShow 4457, hintHide 4458, onbInit 4459, onbPlayed 4461, onbActed 4462, setPlayUI 4464, clearNow 4465, showDrift 4466, magicGlow 4474
- **Scope: a quiet oscilloscope in the house colours** (line 4481): scopeInit 4485, scopeCalm 4489, scopeCols 4490, scopeHit 4491, scopeWake 4492, scopeGrid 4493, scopeTrace 4496, scopeIdle 4498, scopeFrame 4499, draw 4518, makeSegK 4549, makeSelK 4553, makeKnob 4557, editX 4583, kfoldSeen 4593, kfoldHint 4594, laneRow 4598, paintPending 4678, paintCell 4680, editCell 4696, euRow 4708, renderLanes 4723, renderStyles 4735, initTips 4764, initValues 4779, bindMacro 4780, layersLayout 4787, initControls 4807, status 5160, afterLoad 5161, updHist 5162, renderFavs 5163, inflate 5174, loadShared 5175, fileBase 5180
- **EXPORT: WAV** (line 5185): wavBytes 5187, kCoefs 5199, loudness 5204, truePeak 5214, midiBytes 5220, midiBytesX 5221, chLen 5248, chordMidiBytes 5249, CRC 5256, crc32 5257, zipBlob 5260, loopLen 5280, renderLoop 5282, renderLoopX 5283
- **Capture: keep what you just heard** (line 5292): capAttach 5297, capStart 5305, capLog 5306, capWindow 5307, capAudio 5313, capMidi 5317, capture 5327
- **Delivery: a folder you picked (no zip), or a zip download** (line 5340): idb 5342, kvSet 5343, kvGet 5344, outUI 5345, outPick 5346, outReady 5347, writeFiles 5348, deliver 5350, resampleTo 5356
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5358): dwKey 5360, dwPrepare 5361
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5366): jamTrack 5373, jamPut 5374, jamRec 5376, jamStart 5378, jamWorp 5387, jamUI 5390, jamStop 5394, jamWav 5404, jamFiles 5409
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5416): bbUI 5420, bbPick 5421, bbName 5422, bbSend 5426, exportLoop 5446
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5487): m4lAlign 5490, m4lInit 5494
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5526): onBar 5530, qRun 5534, qMark 5536, qDraw 5539
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5544): scenesRender 5546, sceneStore 5557, sceneClear 5558, sceneRecall 5559
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5562): morphCap 5571, morphStart 5573, morphSet 5582, morphInd 5599, morphSnap 5601, scBase 5605, scEdited 5606, morphStep 5609, morphEnd 5611, morphUI 5619, setView 5631
- **script starts** (line 5644): (no functions)

## Worp: public/worp/index.html (1905 lines)

- **script starts** (line 446): $ 448, mtof 459, mod 460
- **seeded dice** (line 462): rng 463, scaleLabel 474, semis 475
- **patch generation: chance inside musical limits** (line 477): genSpectrum 478, fromHist 492, histEntry 493, genName 494, uniqueName 503, genPatch 504
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 627): anchorFrom 645, euclidW 647, genPhraseStyle 648, rnd01 687, phraseAt 690, phraseAt0 692, phCx 700, phZ 701, phraseCore 702, phraseDesc 737, lvSd 746, lvMem 747, lvP2 752, lvCt 753, lvSnap 754, lvBar 755, phraseV2 771, lvMap 782, phraseOut 783
- **the modular part: sources, cables, re-patching** (line 786): genMods 789, genFx 841, fxDesc 869, destRange 878, destName 890, srcDesc 891
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 900): NgomaFilterCore 903, NgomaFilterProc 971, WorpRecProc 982, cutHz 996, loadFilter 997, syncFilter 1004, saveFilter 1008, saveEnv 1011
- **audio graph** (line 1013): makeIR 1015, curve 1028, initAudio 1029, gateStep 1066, prepWaves 1068, applyFx 1075, mixVal 1097, applyMix 1098, loopD 1100, airNorm 1101, foldCurve 1102, bitCurve 1105, quantCurve 1106, chroma 1107, fxRotor 1114, fxBitplane 1122, fxHalo 1129, fxStrings 1147, fxShifter 1155, fxSonar 1169, buildFx 1179, retireFx 1187, globalParams 1191, buildMods 1192, retireMods 1213, modTick 1219, envMul 1255, ampOf 1256, Voice 1259
- **voices** (line 1374): polyOn 1376, polyOff 1381, mono 1382, playRec 1388, playPhrase 1392, releaseAll 1395, liveOn 1401, liveOff 1411, setSustain 1424
- **state** (line 1426): cur 1428, getBpm 1429, newSeed 1430, load 1431, save 1432, setPatch 1434, roll 1449, back 1454, setMode 1458
- **playing by itself** (line 1473): startDrone 1475, evolveDrone 1476, tick 1484, startPlay 1495, stopPlay 1506
- **MIDI** (line 1513): midiStatus 1515, initMIDI 1516, onMidi 1524, renderLearn 1541
- **rendering** (line 1548): noteName 1549, layerDetail 1550, layerTag 1557
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1559): BC 1564, ngomaOpen 1565, linked 1570, outGain 1572, epochToCtx 1573, hostT0 1576, relock 1577, transportSync 1579, worpPost 1587, setPlayUI 1588, hostVoicing 1593, applyHost 1595, hostChanged 1597, renderFollow 1604, focusNgoma 1607, toNgoma 1611, onHostMsg 1612, recStart 1629, recStop 1633, patchCode 1638, fltTok 1641, shareToken 1642, setFLT 1643, setENV 1644, envTok 1645, envNeutral 1646, hearInNgoma 1652, renderLive 1655, parseToken 1658, render 1662, renderFx 1688, renderPatch 1694, renderMusic 1703, lineHas 1720, lineUI 1721, lineSet 1723, drawSteps 1727, recLine 1736, recQ 1744, recFinish 1745, kbStart 1755, buildKb 1756, markKey 1764, ptrUp 1768, togglePlay 1783
- **ring visual** (line 1793): ringAn 1797, draw 1798
- **wiring** (line 1822): renderFilter 1842, secT 1851, renderEnv 1852, fillRange 1898
