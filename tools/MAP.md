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

## Ngoma: public/index.html (5448 lines)

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
- **voices** (line 2067): polyOn 2069, polyOff 2074, mono 2075, playRec 2081, playPhrase 2085, releaseAll 2088, lineAt 2151
- **script starts** (line 2155): (no functions)
- **ENGINE** (line 2181): isMan 2207, kickOn 2208, kickHeld 2209, rnd 2382, euclid 2387, charOf 2392, genSteps 2393, varWeight 2420, mutateSteps 2421, mutateStepsX 2422, variant 2456, anySolo 2461, fillOn 2463, condOk 2465, dlgPalette 2480, dlgPlan 2482, lifeInfo 2506, eventsAt 2513, stepDur 2544, grooveOff 2548, hitsOf 2558, midiNote 2563, mname 2571, inScale 2572, snap 2573, nearestPC 2574
- **STATE** (line 2577): panMig 2583, freshLane 2587, lanesFrom 2594, oOpen 2604, migrateFx 2608, migrateSnap 2611, invalidate 2630, polyLen 2633, regen 2643, regenAll 2648, applyPreset 2649, varyLane 2667, metric 2683, contextOcc 2684, randLane 2691, hasHits 2728, anchorIds 2732, lhlW 2734, syncOf 2736, patternFeatures 2743, sugTargets 2758, scorePattern 2765, hamming 2775, currentPat 2776, makeSuggestions 2777, applySuggestion 2795, hSnap 2803, hApply 2804, hRecord 2805, hStep 2810, favSnap 2812, favLoad 2814, resetBasis 2821, tuneToKey 2827, resetKit 2829, rollKit 2830, rollLane 2835, patternData 2846, kitData 2847, applyPattern 2848, applyKit 2856
- **AUDIO** (line 2868): noiseBuf 2884, env 2885, noise 2886, mtof 2887, bq 2888, tone 2889, cents 2897, vMem 2899, vBell 2931, pulseBuf 2961, vUdu 2967, vTri 2984, vTabla 3003, vBayan 3020, vWood 3030, vTamb 3042, vClap 3062, vShk 3073, driftAt 3084, chokeIn 3092, voice 3096, voiceKind 3108, vcSpec 3130, vcGet 3137, vcPump 3140
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3150): irKey 3161, makeIR 3162, springIR 3189, unityCurve 3201, satCurve 3202, buildReverb 3203, bloomOn 3215, bloomHz 3216, bloomSync 3217, bloomStep 3220, buildDelay 3221, tapeCurve 3250, NgomaFilterCore 3254, NgomaFilterProc 3322, NgomaRecProc 3335, NgomaCombProc 3343, NgomaShimProc 3357, loadFilter 3372, attachFilter 3380, smooth 3399, mgDecK 3401, mgP 3402, buildMagic 3403, presetTrim 3439, magicSync 3440, magicWorklet 3452, combFallback 3458, resChord 3468, resMsg 3477, resStep 3479, resHz 3481, procSync 3482, combStep 3494, formantStep 3500, glitchStep 3505, cosmosErase 3519, padNotes 3529, padRoot 3538, padLoops 3539, softTone 3548, padSc 3561, padNt 3562, chProgOf 3572, chOn 3573, chPer 3574, chSemi 3575, chDegOf 3576, chWander 3578, chordAt 3583, chName 3585, chKey 3587, chTn 3592, chLabel 3598, tideState 3604, padTides 3616, tideTone 3621, echoPhrase 3630, padEchoes 3636, echoTone 3643, seasonChord 3654, seasonHold 3667, padSeasons 3668, warmVoice 3677, subVoice 3684, grain 3687, padRare 3693, buildPad 3701, padCutHz 3716, unitFlt 3720, fltHz 3721, fltFmt 3722, unitWet 3723, unitEcho 3724, unitTr 3725, trDeg 3726, pmtof 3727, wTry 3730, padTy 3731, padLive 3732, padSync 3733, padDrone 3746, droneVoice 3748, worpSeed 3758, padRecOn 3763, stepNow 3764, nrecUI 3765, nrecClicks 3773, nrecToggle 3776, nrecStop 3783, nrecNote 3784, nrecTick 3787, padMine 3793, worpSpec 3794, worpCode 3795, worpFlt 3797, worpToken 3798
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3799): lineMine 3811, recOn 3812, midiConnect 3813, midiPadOK 3820, midiDest 3821, midiShort 3822, midiUI 3823, midiQT 3828, midiKey 3831, ngMidi 3833, midiAuto 3839, leadAnchorTpl 3841, leadAnchorFn 3844, leadLv 3850, leadDrum 3851, leadGain 3853, leadMeasure 3854, buildDub 3864, dubSync 3869, fltQ 3873, buildLead 3874
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3880): fldTrim 3895, fldId 3896, fldInfo 3897, fldKey 3898, fldBuf 3899, fldNorm 3900, fldDecode 3902, fldLoad 3903, fldOwnLoad 3912, fldOwnSet 3914, buildField 3915, fldLive 3919, fldHz 3920, fldStopLoop 3921, fldSync 3922, fldWalk 3929, fldStep 3930, fldDuck 3942, fldUI 3943, leadLive 3947, leadSpec 3948, leadSync 3949, leadEngine 3951, leadBar 3961, lcdSet 3968, leadUI 3969, worpBar 3974, worpUI 3990, worpParse 3996, worpUse 4002, worpHash 4004, WBC 4007, ctxEpoch 4008, worpState 4010, worpPost 4013, worpMsg 4018, worpPanel 4043, padBar 4049, buildGraph 4075, buildRoom 4105, roomSync 4110, clipCurve 4112, vetOn 4114, vetAmt 4115, VET_TRIM 4116, masterCurve 4120, buildVet 4121, vetSync 4135, shaperCurve 4139, lfoHz 4141, lfoPeriod 4142, cutPos 4143, cutHz 4144, syncFx 4145, pv 4175, syncGraph 4176, animCurve 4182, animValues 4184, applyAnim 4186, animLive 4192, fxTail 4194, flamGuard 4207, mgQ 4212, scheduleStep 4213, evN 4239, hitGate 4240, AUD 4249, STABLE 4250, loadLate 4251, stableSet 4252, ensureCtx 4255, tick 4256, start 4261, stop 4263, setDrop 4269, setDrumsOff 4272, dropApply 4273, dropMask 4278, preview 4279, $ 4286, mvolGain 4288, setMvol 4289, initMvol 4293, flashLed 4299
- **First visit: invite to press Play, then one next step** (line 4305): onbSave 4308, hintShow 4309, hintHide 4310, onbInit 4311, onbPlayed 4313, onbActed 4314, setPlayUI 4316, clearNow 4317, showDrift 4318, magicGlow 4326
- **Scope: a quiet oscilloscope in the house colours** (line 4333): scopeInit 4337, scopeCalm 4341, scopeCols 4342, scopeHit 4343, scopeWake 4344, scopeGrid 4345, scopeTrace 4348, scopeIdle 4350, scopeFrame 4351, draw 4370, makeSegK 4401, makeSelK 4405, makeKnob 4409, editX 4435, kfoldSeen 4445, kfoldHint 4446, laneRow 4450, paintPending 4530, paintCell 4532, editCell 4548, euRow 4560, renderLanes 4575, renderStyles 4587, initTips 4616, initValues 4631, bindMacro 4632, initControls 4636, status 4964, afterLoad 4965, updHist 4966, renderFavs 4967, inflate 4978, loadShared 4979, fileBase 4984
- **EXPORT: WAV** (line 4989): wavBytes 4991, kCoefs 5003, loudness 5008, truePeak 5018, midiBytes 5024, midiBytesX 5025, chLen 5052, chordMidiBytes 5053, CRC 5060, crc32 5061, zipBlob 5062, loopLen 5082, renderLoop 5084, renderLoopX 5085
- **Capture: keep what you just heard** (line 5094): capAttach 5099, capStart 5107, capLog 5108, capWindow 5109, capAudio 5115, capMidi 5119, capture 5129
- **Delivery: a folder you picked (no zip), or a zip download** (line 5142): idb 5144, kvSet 5145, kvGet 5146, outUI 5147, outPick 5148, outReady 5149, writeFiles 5150, deliver 5152, resampleTo 5158
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5160): dwKey 5162, dwPrepare 5163
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5168): jamTrack 5175, jamPut 5176, jamRec 5178, jamStart 5180, jamWorp 5189, jamUI 5192, jamStop 5196, jamWav 5206, jamFiles 5211
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5218): bbUI 5222, bbPick 5223, bbName 5224, bbSend 5228, exportLoop 5248
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5289): m4lAlign 5292, m4lInit 5296
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5328): onBar 5332, qRun 5336, qMark 5338, qDraw 5341
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5346): scenesRender 5348, sceneStore 5359, sceneClear 5360, sceneRecall 5361
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5364): morphCap 5373, morphStart 5375, morphSet 5384, morphInd 5401, morphSnap 5403, scBase 5407, scEdited 5408, morphStep 5411, morphEnd 5413, morphUI 5421, setView 5433

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
