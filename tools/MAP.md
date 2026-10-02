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

## Ngoma: public/index.html (5634 lines)

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
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3886): lineMine 3898, recOn 3899, midiConnect 3900, midiPadOK 3907, midiDest 3908, midiShort 3909, midiUI 3910, midiQT 3915, midiKey 3918, ngMidi 3920, midiAuto 3926, leadAnchorTpl 3928, leadAnchorFn 3931, leadLen 3937, leadLv 3938, leadDrum 3939, plPatch 3949, plMove 3955, plBytes 3960, plEngine 3961, plSync 3964, plNote 3966, plKeys 3968, plPhrase 3971, plSemi 3972, plRec 3974, plBar 3976, leadGain 3982, buildDub 3986, dubSync 3991, fltQ 3995, buildLead 3996
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 4002): fldTrim 4017, fldId 4018, fldInfo 4019, fldKey 4020, fldBuf 4021, fldNorm 4022, fldDecode 4024, fldLoad 4025, fldOwnLoad 4034, fldOwnSet 4036, buildField 4037, fldLive 4041, fldHz 4042, fldStopLoop 4043, fldSync 4044, fldWalk 4051, fldStep 4052, fldDuck 4064, fldUI 4065
- **Candy (v180; Jesse: ear candy instead of a big texture: small sounds without a key that ma** (line 4069): buildCandy 4074, cdLive 4075, cdSeed 4076, cdSrc 4077, cdFid 4078, cdBuf 4079, cdSync 4080, cdPalette 4084, cdHit 4089, cdStep 4098, cdUI 4105, leadLive 4107, leadSpec 4108, leadSync 4109, leadBar 4111, lcdSet 4114, leadUI 4115, worpBar 4119, worpUI 4135, worpParse 4141, worpUse 4147, worpHash 4149, WBC 4152, ctxEpoch 4153, worpState 4155, worpPost 4158, worpMsg 4163, worpPanel 4182, padBar 4188, buildGraph 4214, buildRoom 4244, roomSync 4249, clipCurve 4251, vetOn 4253, vetAmt 4254, VET_TRIM 4255, masterCurve 4259, buildVet 4260, vetSync 4274, shaperCurve 4278, lfoHz 4280, lfoPeriod 4281, cutPos 4282, cutHz 4283, syncFx 4284, pv 4314, syncGraph 4315, animCurve 4321, animValues 4323, applyAnim 4325, animLive 4331, fxTail 4333, flamGuard 4346, mgQ 4351, scheduleStep 4352, evN 4378, hitGate 4379, AUD 4388, STABLE 4389, loadLate 4390, stableSet 4391, ensureCtx 4394, tick 4395, start 4400, stop 4402, setDrop 4407, setDrumsOff 4410, dropApply 4411, dropMask 4416, preview 4417, $ 4424, mvolGain 4426, setMvol 4427, initMvol 4431, flashLed 4437
- **First visit: invite to press Play, then one next step** (line 4443): onbSave 4446, hintShow 4447, hintHide 4448, onbInit 4449, onbPlayed 4451, onbActed 4452, setPlayUI 4454, clearNow 4455, showDrift 4456, magicGlow 4464
- **Scope: a quiet oscilloscope in the house colours** (line 4471): scopeInit 4475, scopeCalm 4479, scopeCols 4480, scopeHit 4481, scopeWake 4482, scopeGrid 4483, scopeTrace 4486, scopeIdle 4488, scopeFrame 4489, draw 4508, makeSegK 4539, makeSelK 4543, makeKnob 4547, editX 4573, kfoldSeen 4583, kfoldHint 4584, laneRow 4588, paintPending 4668, paintCell 4670, editCell 4686, euRow 4698, renderLanes 4713, renderStyles 4725, initTips 4754, initValues 4769, bindMacro 4770, layersLayout 4777, initControls 4797, status 5149, afterLoad 5150, updHist 5151, renderFavs 5152, inflate 5163, loadShared 5164, fileBase 5169
- **EXPORT: WAV** (line 5174): wavBytes 5176, kCoefs 5188, loudness 5193, truePeak 5203, midiBytes 5209, midiBytesX 5210, chLen 5237, chordMidiBytes 5238, CRC 5245, crc32 5246, zipBlob 5247, loopLen 5267, renderLoop 5269, renderLoopX 5270
- **Capture: keep what you just heard** (line 5279): capAttach 5284, capStart 5292, capLog 5293, capWindow 5294, capAudio 5300, capMidi 5304, capture 5314
- **Delivery: a folder you picked (no zip), or a zip download** (line 5327): idb 5329, kvSet 5330, kvGet 5331, outUI 5332, outPick 5333, outReady 5334, writeFiles 5335, deliver 5337, resampleTo 5343
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5345): dwKey 5347, dwPrepare 5348
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5353): jamTrack 5360, jamPut 5361, jamRec 5363, jamStart 5365, jamWorp 5374, jamUI 5377, jamStop 5381, jamWav 5391, jamFiles 5396
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5403): bbUI 5407, bbPick 5408, bbName 5409, bbSend 5413, exportLoop 5433
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5474): m4lAlign 5477, m4lInit 5481
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5513): onBar 5517, qRun 5521, qMark 5523, qDraw 5526
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5531): scenesRender 5533, sceneStore 5544, sceneClear 5545, sceneRecall 5546
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5549): morphCap 5558, morphStart 5560, morphSet 5569, morphInd 5586, morphSnap 5588, scBase 5592, scEdited 5593, morphStep 5596, morphEnd 5598, morphUI 5606, setView 5618
- **script starts** (line 5631): (no functions)

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
