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

## Ngoma: public/index.html (5169 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 447): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 472): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 493): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 504): (no functions)
- **Scenes (v91)** (line 517): (no functions)
- **Changes on the next bar (v88)** (line 544): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 554): (no functions)
- **script starts** (line 1274): mtof 1289, mod 1290
- **seeded dice** (line 1292): rng 1293, scaleLabel 1304, semis 1305
- **patch generation: chance inside musical limits** (line 1307): genSpectrum 1308, fromHist 1322, histEntry 1323, genName 1324, uniqueName 1333, genPatch 1334
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1436): anchorFrom 1452, euclidW 1454, genPhraseStyle 1455, rnd01 1488, phraseAt 1491, phraseAt0 1493, phCx 1501, phZ 1502, phraseCore 1503, phraseDesc 1533
- **the modular part: sources, cables, re-patching** (line 1535): genMods 1538, genFx 1590, fxDesc 1618, destRange 1627, destName 1639, srcDesc 1640, create 1650, makeIR 1657, curve 1670, initGraph 1671, gateStep 1702, prepWaves 1704, applyFx 1711, mixVal 1733, applyMix 1734, loopD 1736, airNorm 1737, foldCurve 1738, bitCurve 1741, quantCurve 1742, chroma 1743, fxRotor 1750, fxBitplane 1758, fxHalo 1765, fxStrings 1783, fxShifter 1791, fxSonar 1805, buildFx 1815, retireFx 1823, globalParams 1827, buildMods 1828, retireMods 1849, modTick 1855, envMul 1891, ampOf 1892, Voice 1895
- **voices** (line 2010): polyOn 2012, polyOff 2017, mono 2018, playRec 2024, playPhrase 2028, releaseAll 2031
- **script starts** (line 2093): (no functions)
- **ENGINE** (line 2119): isMan 2145, kickOn 2146, kickHeld 2147, rnd 2299, euclid 2304, charOf 2309, genSteps 2310, varWeight 2337, mutateSteps 2338, mutateStepsX 2339, variant 2373, anySolo 2378, fillOn 2380, condOk 2382, dlgPalette 2397, dlgPlan 2399, lifeInfo 2423, eventsAt 2430, stepDur 2461, grooveOff 2465, hitsOf 2475, midiNote 2480, mname 2488, inScale 2489, snap 2490, nearestPC 2491
- **STATE** (line 2494): panMig 2500, freshLane 2504, lanesFrom 2511, oOpen 2521, migrateFx 2525, migrateSnap 2528, invalidate 2547, polyLen 2550, regen 2559, regenAll 2564, applyPreset 2565, varyLane 2583, metric 2599, contextOcc 2600, randLane 2607, hasHits 2644, anchorIds 2648, lhlW 2650, syncOf 2652, patternFeatures 2659, sugTargets 2674, scorePattern 2681, hamming 2691, currentPat 2692, makeSuggestions 2693, applySuggestion 2711, hSnap 2719, hApply 2720, hRecord 2721, hStep 2726, favSnap 2728, favLoad 2730, resetBasis 2737, tuneToKey 2743, resetKit 2745, rollKit 2746, rollLane 2751, patternData 2762, kitData 2763, applyPattern 2764, applyKit 2772
- **AUDIO** (line 2784): noiseBuf 2800, env 2801, noise 2802, mtof 2803, bq 2804, tone 2805, cents 2813, vMem 2815, vBell 2847, pulseBuf 2877, vUdu 2883, vTri 2900, vTabla 2919, vBayan 2936, vWood 2946, vTamb 2958, vClap 2978, vShk 2989, driftAt 3000, chokeIn 3008, voice 3012, voiceKind 3024, vcSpec 3046, vcGet 3053, vcPump 3056
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3066): irKey 3077, makeIR 3078, springIR 3105, unityCurve 3117, satCurve 3118, buildReverb 3119, bloomOn 3131, bloomHz 3132, bloomSync 3133, bloomStep 3136, buildDelay 3137, tapeCurve 3166, NgomaFilterCore 3170, NgomaFilterProc 3238, NgomaRecProc 3251, NgomaCombProc 3259, NgomaShimProc 3273, loadFilter 3288, attachFilter 3296, smooth 3315, mgDecK 3317, mgP 3318, buildMagic 3319, presetTrim 3355, magicSync 3356, magicWorklet 3368, combFallback 3374, resChord 3384, resMsg 3393, resStep 3395, resHz 3397, procSync 3398, combStep 3407, formantStep 3413, glitchStep 3418, cosmosErase 3432, padNotes 3442, padRoot 3451, padLoops 3452, softTone 3461, padSc 3474, padNt 3475, chProgOf 3485, chOn 3486, chPer 3487, chSemi 3488, chDegOf 3489, chWander 3491, chordAt 3496, chName 3498, chKey 3500, chTn 3505, chLabel 3511, tideState 3517, padTides 3529, tideTone 3534, echoPhrase 3543, padEchoes 3549, echoTone 3556, seasonChord 3567, seasonHold 3580, padSeasons 3581, warmVoice 3590, subVoice 3597, grain 3600, padRare 3606, buildPad 3614, padCutHz 3628, unitFlt 3632, fltHz 3633, fltFmt 3634, unitWet 3635, unitEcho 3636, unitTr 3637, trDeg 3638, pmtof 3639, wTry 3642, padTy 3643, padLive 3644, padSync 3645, padDrone 3654, droneVoice 3656, worpSeed 3666, worpSpec 3667, worpCode 3668, worpFlt 3670, worpToken 3671
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3672): lineMine 3684, recOn 3685, midiConnect 3686, midiPadOK 3693, midiDest 3694, midiShort 3695, midiUI 3696, midiQT 3701, midiKey 3704, ngMidi 3706, midiAuto 3711, leadAnchorTpl 3713, leadAnchorFn 3716, leadGain 3718, leadMeasure 3719, buildDub 3729, dubSync 3734, fltQ 3738, buildLead 3739, leadLive 3740, leadSpec 3741, leadSync 3742, leadEngine 3744, leadBar 3754, lcdSet 3761, leadUI 3762, worpBar 3767, worpUI 3782, worpParse 3787, worpUse 3793, worpHash 3795, WBC 3798, ctxEpoch 3799, worpState 3801, worpPost 3804, worpMsg 3809, worpPanel 3834, padBar 3840, buildGraph 3866, buildRoom 3896, roomSync 3901, clipCurve 3903, vetOn 3905, vetAmt 3906, VET_TRIM 3907, masterCurve 3911, buildVet 3912, vetSync 3926, shaperCurve 3930, lfoHz 3932, lfoPeriod 3933, cutPos 3934, cutHz 3935, syncFx 3936, pv 3966, syncGraph 3967, animCurve 3973, animValues 3975, applyAnim 3977, animLive 3983, fxTail 3985, flamGuard 3997, mgQ 4002, scheduleStep 4003, evN 4029, hitGate 4030, STABLE 4038, loadLate 4039, stableSet 4040, ensureCtx 4043, tick 4044, start 4049, stop 4051, setDrop 4057, setDrumsOff 4060, dropApply 4061, dropMask 4066, preview 4067, $ 4074, mvolGain 4076, setMvol 4077, initMvol 4081, flashLed 4087
- **First visit: invite to press Play, then one next step** (line 4093): onbSave 4096, hintShow 4097, hintHide 4098, onbInit 4099, onbPlayed 4101, onbActed 4102, setPlayUI 4104, clearNow 4105, showDrift 4106, magicGlow 4114
- **Scope: a quiet oscilloscope in the house colours** (line 4121): scopeInit 4125, scopeCalm 4129, scopeCols 4130, scopeHit 4131, scopeWake 4132, scopeGrid 4133, scopeTrace 4136, scopeIdle 4138, scopeFrame 4139, draw 4158, makeSegK 4189, makeSelK 4193, makeKnob 4197, editX 4223, kfoldSeen 4233, kfoldHint 4234, laneRow 4238, paintPending 4318, paintCell 4320, editCell 4336, euRow 4348, renderLanes 4363, renderStyles 4375, initTips 4404, initValues 4419, bindMacro 4420, initControls 4424, status 4698, afterLoad 4699, updHist 4700, renderFavs 4701, inflate 4712, loadShared 4713, fileBase 4718
- **EXPORT: WAV** (line 4723): wavBytes 4725, kCoefs 4737, loudness 4742, truePeak 4752, midiBytes 4758, midiBytesX 4759, CRC 4784, crc32 4785, zipBlob 4786, loopLen 4806, renderLoop 4808, renderLoopX 4809
- **Capture: keep what you just heard** (line 4818): capAttach 4823, capStart 4831, capLog 4832, capWindow 4833, capAudio 4839, capMidi 4843, capture 4853
- **Delivery: a folder you picked (no zip), or a zip download** (line 4866): idb 4868, kvSet 4869, kvGet 4870, outUI 4871, outPick 4872, outReady 4873, writeFiles 4874, deliver 4876, resampleTo 4882
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 4884): dwKey 4886, dwPrepare 4887
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 4892): jamTrack 4899, jamPut 4900, jamRec 4902, jamStart 4904, jamWorp 4913, jamUI 4916, jamStop 4920, jamWav 4930, jamFiles 4935
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 4942): bbUI 4946, bbPick 4947, bbName 4948, bbSend 4952, exportLoop 4972
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5010): m4lAlign 5013, m4lInit 5017
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5049): onBar 5053, qRun 5057, qMark 5059, qDraw 5062
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5067): scenesRender 5069, sceneStore 5080, sceneClear 5081, sceneRecall 5082
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5085): morphCap 5094, morphStart 5096, morphSet 5105, morphInd 5122, morphSnap 5124, scBase 5128, scEdited 5129, morphStep 5132, morphEnd 5134, morphUI 5142, setView 5154

## Worp: public/worp/index.html (1678 lines)

- **script starts** (line 307): $ 309, mtof 320, mod 321
- **seeded dice** (line 323): rng 324, scaleLabel 335, semis 336
- **patch generation: chance inside musical limits** (line 338): genSpectrum 339, fromHist 353, histEntry 354, genName 355, uniqueName 364, genPatch 365
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 467): anchorFrom 483, euclidW 485, genPhraseStyle 486, rnd01 519, phraseAt 522, phraseAt0 524, phCx 532, phZ 533, phraseCore 534, phraseDesc 564
- **the modular part: sources, cables, re-patching** (line 566): genMods 569, genFx 621, fxDesc 649, destRange 658, destName 670, srcDesc 671
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 680): NgomaFilterCore 683, NgomaFilterProc 751, WorpRecProc 762, cutHz 776, loadFilter 777, syncFilter 784, saveFilter 788, saveEnv 791
- **audio graph** (line 793): makeIR 795, curve 808, initAudio 809, gateStep 846, prepWaves 848, applyFx 855, mixVal 877, applyMix 878, loopD 880, airNorm 881, foldCurve 882, bitCurve 885, quantCurve 886, chroma 887, fxRotor 894, fxBitplane 902, fxHalo 909, fxStrings 927, fxShifter 935, fxSonar 949, buildFx 959, retireFx 967, globalParams 971, buildMods 972, retireMods 993, modTick 999, envMul 1035, ampOf 1036, Voice 1039
- **voices** (line 1154): polyOn 1156, polyOff 1161, mono 1162, playRec 1168, playPhrase 1172, releaseAll 1175, liveOn 1181, liveOff 1191, setSustain 1204
- **state** (line 1206): cur 1208, getBpm 1209, newSeed 1210, load 1211, save 1212, setPatch 1214, roll 1229, back 1234, setMode 1238
- **playing by itself** (line 1252): startDrone 1254, evolveDrone 1255, tick 1263, startPlay 1274, stopPlay 1285
- **MIDI** (line 1292): midiStatus 1294, initMIDI 1295, onMidi 1303, renderLearn 1320
- **rendering** (line 1327): noteName 1328, layerDetail 1329, layerTag 1336
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1338): BC 1343, ngomaOpen 1344, linked 1349, outGain 1351, epochToCtx 1352, hostT0 1355, relock 1356, transportSync 1358, worpPost 1366, setPlayUI 1367, hostVoicing 1372, applyHost 1374, hostChanged 1376, renderFollow 1383, focusNgoma 1386, toNgoma 1390, onHostMsg 1391, recStart 1407, recStop 1411, patchCode 1416, fltTok 1419, shareToken 1420, setFLT 1421, setENV 1422, envTok 1423, envNeutral 1424, hearInNgoma 1430, renderLive 1433, parseToken 1436, render 1440, renderFx 1466, renderPatch 1472, renderMusic 1481, lineHas 1498, lineUI 1499, lineSet 1501, drawSteps 1505, recLine 1514, recQ 1522, recFinish 1523, kbStart 1533, buildKb 1534, markKey 1542, ptrUp 1546, togglePlay 1561
- **ring visual** (line 1571): ringAn 1575, draw 1576
- **wiring** (line 1600): renderFilter 1620, secT 1629, renderEnv 1630
