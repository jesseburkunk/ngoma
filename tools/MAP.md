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

## Ngoma: public/index.html (5508 lines)

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
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3833): lineMine 3845, recOn 3846, midiConnect 3847, midiPadOK 3854, midiDest 3855, midiShort 3856, midiUI 3857, midiQT 3862, midiKey 3865, ngMidi 3867, midiAuto 3873, leadAnchorTpl 3875, leadAnchorFn 3878, leadLv 3884, leadDrum 3885, plPatch 3895, plMove 3901, plBytes 3906, plEngine 3907, plSync 3910, plNote 3912, plKeys 3914, plPhrase 3917, plSemi 3918, plRec 3920, plBar 3922, leadGain 3928, buildDub 3932, dubSync 3937, fltQ 3941, buildLead 3942
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3948): fldTrim 3963, fldId 3964, fldInfo 3965, fldKey 3966, fldBuf 3967, fldNorm 3968, fldDecode 3970, fldLoad 3971, fldOwnLoad 3980, fldOwnSet 3982, buildField 3983, fldLive 3987, fldHz 3988, fldStopLoop 3989, fldSync 3990, fldWalk 3997, fldStep 3998, fldDuck 4010, fldUI 4011, leadLive 4015, leadSpec 4016, leadSync 4017, leadBar 4019, lcdSet 4022, leadUI 4023, worpBar 4027, worpUI 4043, worpParse 4049, worpUse 4055, worpHash 4057, WBC 4060, ctxEpoch 4061, worpState 4063, worpPost 4066, worpMsg 4071, worpPanel 4090, padBar 4096, buildGraph 4122, buildRoom 4152, roomSync 4157, clipCurve 4159, vetOn 4161, vetAmt 4162, VET_TRIM 4163, masterCurve 4167, buildVet 4168, vetSync 4182, shaperCurve 4186, lfoHz 4188, lfoPeriod 4189, cutPos 4190, cutHz 4191, syncFx 4192, pv 4222, syncGraph 4223, animCurve 4229, animValues 4231, applyAnim 4233, animLive 4239, fxTail 4241, flamGuard 4254, mgQ 4259, scheduleStep 4260, evN 4286, hitGate 4287, AUD 4296, STABLE 4297, loadLate 4298, stableSet 4299, ensureCtx 4302, tick 4303, start 4308, stop 4310, setDrop 4315, setDrumsOff 4318, dropApply 4319, dropMask 4324, preview 4325, $ 4332, mvolGain 4334, setMvol 4335, initMvol 4339, flashLed 4345
- **First visit: invite to press Play, then one next step** (line 4351): onbSave 4354, hintShow 4355, hintHide 4356, onbInit 4357, onbPlayed 4359, onbActed 4360, setPlayUI 4362, clearNow 4363, showDrift 4364, magicGlow 4372
- **Scope: a quiet oscilloscope in the house colours** (line 4379): scopeInit 4383, scopeCalm 4387, scopeCols 4388, scopeHit 4389, scopeWake 4390, scopeGrid 4391, scopeTrace 4394, scopeIdle 4396, scopeFrame 4397, draw 4416, makeSegK 4447, makeSelK 4451, makeKnob 4455, editX 4481, kfoldSeen 4491, kfoldHint 4492, laneRow 4496, paintPending 4576, paintCell 4578, editCell 4594, euRow 4606, renderLanes 4621, renderStyles 4633, initTips 4662, initValues 4677, bindMacro 4678, initControls 4682, status 5023, afterLoad 5024, updHist 5025, renderFavs 5026, inflate 5037, loadShared 5038, fileBase 5043
- **EXPORT: WAV** (line 5048): wavBytes 5050, kCoefs 5062, loudness 5067, truePeak 5077, midiBytes 5083, midiBytesX 5084, chLen 5111, chordMidiBytes 5112, CRC 5119, crc32 5120, zipBlob 5121, loopLen 5141, renderLoop 5143, renderLoopX 5144
- **Capture: keep what you just heard** (line 5153): capAttach 5158, capStart 5166, capLog 5167, capWindow 5168, capAudio 5174, capMidi 5178, capture 5188
- **Delivery: a folder you picked (no zip), or a zip download** (line 5201): idb 5203, kvSet 5204, kvGet 5205, outUI 5206, outPick 5207, outReady 5208, writeFiles 5209, deliver 5211, resampleTo 5217
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5219): dwKey 5221, dwPrepare 5222
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5227): jamTrack 5234, jamPut 5235, jamRec 5237, jamStart 5239, jamWorp 5248, jamUI 5251, jamStop 5255, jamWav 5265, jamFiles 5270
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5277): bbUI 5281, bbPick 5282, bbName 5283, bbSend 5287, exportLoop 5307
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5348): m4lAlign 5351, m4lInit 5355
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5387): onBar 5391, qRun 5395, qMark 5397, qDraw 5400
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5405): scenesRender 5407, sceneStore 5418, sceneClear 5419, sceneRecall 5420
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5423): morphCap 5432, morphStart 5434, morphSet 5443, morphInd 5460, morphSnap 5462, scBase 5466, scEdited 5467, morphStep 5470, morphEnd 5472, morphUI 5480, setView 5492
- **script starts** (line 5505): (no functions)

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
