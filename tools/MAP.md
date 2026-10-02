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

## Ngoma: public/index.html (5554 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1292): mtof 1307, mod 1308
- **seeded dice** (line 1310): rng 1311, scaleLabel 1322, semis 1323
- **patch generation: chance inside musical limits** (line 1325): genSpectrum 1326, fromHist 1340, histEntry 1341, genName 1342, uniqueName 1351, genPatch 1352
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1475): anchorFrom 1493, euclidW 1495, genPhraseStyle 1496, rnd01 1535, phraseAt 1538, phraseAt0 1540, phCx 1548, phZ 1549, phraseCore 1550, phraseDesc 1585, lvSd 1594, lvMem 1595, lvP2 1600, lvCt 1601, lvSnap 1602, lvBar 1603, phraseV2 1619, phraseOut 1627
- **the modular part: sources, cables, re-patching** (line 1629): genMods 1632, genFx 1684, fxDesc 1712, destRange 1721, destName 1733, srcDesc 1734, create 1744, makeIR 1751, curve 1764, initGraph 1765, gateStep 1796, prepWaves 1798, applyFx 1805, mixVal 1827, applyMix 1828, loopD 1830, airNorm 1831, foldCurve 1832, bitCurve 1835, quantCurve 1836, chroma 1837, fxRotor 1844, fxBitplane 1852, fxHalo 1859, fxStrings 1877, fxShifter 1885, fxSonar 1899, buildFx 1909, retireFx 1917, globalParams 1921, buildMods 1922, retireMods 1943, modTick 1949, envMul 1985, ampOf 1986, Voice 1989
- **voices** (line 2104): polyOn 2106, polyOff 2111, mono 2112, playRec 2118, playPhrase 2122, releaseAll 2125, lineAt 2188, setHostScale 2189
- **script starts** (line 2193): (no functions)
- **ENGINE** (line 2219): isMan 2245, kickOn 2246, kickHeld 2247, rnd 2420, euclid 2425, charOf 2430, genSteps 2431, varWeight 2458, mutateSteps 2459, mutateStepsX 2460, variant 2494, anySolo 2499, fillOn 2501, condOk 2503, dlgPalette 2518, dlgPlan 2520, lifeInfo 2544, eventsAt 2551, stepDur 2582, grooveOff 2586, hitsOf 2596, midiNote 2601, mname 2609, inScale 2610, snap 2611, nearestPC 2612
- **STATE** (line 2615): panMig 2621, freshLane 2625, lanesFrom 2632, oOpen 2642, migrateFx 2646, migrateSnap 2649, invalidate 2668, polyLen 2671, regen 2681, regenAll 2686, applyPreset 2687, varyLane 2705, metric 2721, contextOcc 2722, randLane 2729, hasHits 2766, anchorIds 2770, lhlW 2772, syncOf 2774, patternFeatures 2781, sugTargets 2796, scorePattern 2803, hamming 2813, currentPat 2814, makeSuggestions 2815, applySuggestion 2833, hSnap 2841, hApply 2842, hRecord 2843, hStep 2848, favSnap 2850, favLoad 2852, resetBasis 2859, tuneToKey 2865, resetKit 2867, rollKit 2868, rollLane 2873, patternData 2884, kitData 2885, applyPattern 2886, applyKit 2894
- **AUDIO** (line 2906): noiseBuf 2922, env 2923, noise 2924, mtof 2925, bq 2926, tone 2927, cents 2935, vMem 2937, vBell 2969, pulseBuf 2999, vUdu 3005, vTri 3022, vTabla 3041, vBayan 3058, vWood 3068, vTamb 3080, vClap 3100, vShk 3111, driftAt 3122, chokeIn 3130, voice 3134, voiceKind 3146, vcSpec 3168, vcGet 3175, vcPump 3178
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3188): irKey 3199, makeIR 3200, springIR 3227, unityCurve 3239, satCurve 3240, buildReverb 3241, bloomOn 3253, bloomHz 3254, bloomSync 3255, bloomStep 3258, buildDelay 3259, tapeCurve 3288, NgomaFilterCore 3292, NgomaFilterProc 3360, NgomaRecProc 3373, NgomaCombProc 3381, NgomaShimProc 3395, NgomaPlaitsProc 3406, loadFilter 3433, attachFilter 3441, smooth 3460, mgDecK 3462, mgP 3463, buildMagic 3464, presetTrim 3500, magicSync 3501, magicWorklet 3513, combFallback 3519, resChord 3529, resMsg 3538, resStep 3540, resHz 3542, procSync 3543, combStep 3555, formantStep 3561, glitchStep 3566, cosmosErase 3580, padNotes 3590, padRoot 3599, padLoops 3600, softTone 3609, padSc 3622, padNt 3623, chProgOf 3633, chOn 3634, chPer 3635, chSemi 3636, chDegOf 3637, chWander 3639, chordAt 3644, chName 3646, chKey 3648, chTn 3653, chLabel 3659, tideState 3665, padTides 3677, tideTone 3682, echoPhrase 3691, padEchoes 3697, echoTone 3704, seasonChord 3715, seasonHold 3728, padSeasons 3729, warmVoice 3738, subVoice 3745, grain 3748, padRare 3754, buildPad 3762, padCutHz 3777, unitFlt 3781, fltHz 3782, fltFmt 3783, unitWet 3784, unitEcho 3785, unitTr 3786, trDeg 3787, pmtof 3788, wTry 3791, padTy 3792, padLive 3793, padSync 3794, padDrone 3807, droneVoice 3809, worpSeed 3819, padRecOn 3824, stepNow 3825, nrecUI 3826, nrecClicks 3834, nrecToggle 3837, nrecStop 3844, nrecNote 3845, nrecTick 3848, padMine 3854, worpSpec 3855, worpCode 3856, worpFlt 3858, worpToken 3859
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3860): lineMine 3872, recOn 3873, midiConnect 3874, midiPadOK 3881, midiDest 3882, midiShort 3883, midiUI 3884, midiQT 3889, midiKey 3892, ngMidi 3894, midiAuto 3900, leadAnchorTpl 3902, leadAnchorFn 3905, leadLv 3911, leadDrum 3912, plPatch 3922, plMove 3928, plBytes 3933, plEngine 3934, plSync 3937, plNote 3939, plKeys 3941, plPhrase 3944, plSemi 3945, plRec 3947, plBar 3949, leadGain 3955, buildDub 3959, dubSync 3964, fltQ 3968, buildLead 3969
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3975): fldTrim 3990, fldId 3991, fldInfo 3992, fldKey 3993, fldBuf 3994, fldNorm 3995, fldDecode 3997, fldLoad 3998, fldOwnLoad 4007, fldOwnSet 4009, buildField 4010, fldLive 4014, fldHz 4015, fldStopLoop 4016, fldSync 4017, fldWalk 4024, fldStep 4025, fldDuck 4037, fldUI 4038, leadLive 4042, leadSpec 4043, leadSync 4044, leadBar 4046, lcdSet 4049, leadUI 4050, worpBar 4054, worpUI 4070, worpParse 4076, worpUse 4082, worpHash 4084, WBC 4087, ctxEpoch 4088, worpState 4090, worpPost 4093, worpMsg 4098, worpPanel 4117, padBar 4123, buildGraph 4149, buildRoom 4179, roomSync 4184, clipCurve 4186, vetOn 4188, vetAmt 4189, VET_TRIM 4190, masterCurve 4194, buildVet 4195, vetSync 4209, shaperCurve 4213, lfoHz 4215, lfoPeriod 4216, cutPos 4217, cutHz 4218, syncFx 4219, pv 4249, syncGraph 4250, animCurve 4256, animValues 4258, applyAnim 4260, animLive 4266, fxTail 4268, flamGuard 4281, mgQ 4286, scheduleStep 4287, evN 4313, hitGate 4314, AUD 4323, STABLE 4324, loadLate 4325, stableSet 4326, ensureCtx 4329, tick 4330, start 4335, stop 4337, setDrop 4342, setDrumsOff 4345, dropApply 4346, dropMask 4351, preview 4352, $ 4359, mvolGain 4361, setMvol 4362, initMvol 4366, flashLed 4372
- **First visit: invite to press Play, then one next step** (line 4378): onbSave 4381, hintShow 4382, hintHide 4383, onbInit 4384, onbPlayed 4386, onbActed 4387, setPlayUI 4389, clearNow 4390, showDrift 4391, magicGlow 4399
- **Scope: a quiet oscilloscope in the house colours** (line 4406): scopeInit 4410, scopeCalm 4414, scopeCols 4415, scopeHit 4416, scopeWake 4417, scopeGrid 4418, scopeTrace 4421, scopeIdle 4423, scopeFrame 4424, draw 4443, makeSegK 4474, makeSelK 4478, makeKnob 4482, editX 4508, kfoldSeen 4518, kfoldHint 4519, laneRow 4523, paintPending 4603, paintCell 4605, editCell 4621, euRow 4633, renderLanes 4648, renderStyles 4660, initTips 4689, initValues 4704, bindMacro 4705, layersLayout 4712, initControls 4728, status 5069, afterLoad 5070, updHist 5071, renderFavs 5072, inflate 5083, loadShared 5084, fileBase 5089
- **EXPORT: WAV** (line 5094): wavBytes 5096, kCoefs 5108, loudness 5113, truePeak 5123, midiBytes 5129, midiBytesX 5130, chLen 5157, chordMidiBytes 5158, CRC 5165, crc32 5166, zipBlob 5167, loopLen 5187, renderLoop 5189, renderLoopX 5190
- **Capture: keep what you just heard** (line 5199): capAttach 5204, capStart 5212, capLog 5213, capWindow 5214, capAudio 5220, capMidi 5224, capture 5234
- **Delivery: a folder you picked (no zip), or a zip download** (line 5247): idb 5249, kvSet 5250, kvGet 5251, outUI 5252, outPick 5253, outReady 5254, writeFiles 5255, deliver 5257, resampleTo 5263
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5265): dwKey 5267, dwPrepare 5268
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5273): jamTrack 5280, jamPut 5281, jamRec 5283, jamStart 5285, jamWorp 5294, jamUI 5297, jamStop 5301, jamWav 5311, jamFiles 5316
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5323): bbUI 5327, bbPick 5328, bbName 5329, bbSend 5333, exportLoop 5353
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5394): m4lAlign 5397, m4lInit 5401
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5433): onBar 5437, qRun 5441, qMark 5443, qDraw 5446
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5451): scenesRender 5453, sceneStore 5464, sceneClear 5465, sceneRecall 5466
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5469): morphCap 5478, morphStart 5480, morphSet 5489, morphInd 5506, morphSnap 5508, scBase 5512, scEdited 5513, morphStep 5516, morphEnd 5518, morphUI 5526, setView 5538
- **script starts** (line 5551): (no functions)

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
