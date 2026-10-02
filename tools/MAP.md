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

## Ngoma: public/index.html (5356 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1257): mtof 1272, mod 1273
- **seeded dice** (line 1275): rng 1276, scaleLabel 1287, semis 1288
- **patch generation: chance inside musical limits** (line 1290): genSpectrum 1291, fromHist 1305, histEntry 1306, genName 1307, uniqueName 1316, genPatch 1317
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1425): anchorFrom 1443, euclidW 1445, genPhraseStyle 1446, rnd01 1485, phraseAt 1488, phraseAt0 1490, phCx 1498, phZ 1499, phraseCore 1500, phraseDesc 1535
- **the modular part: sources, cables, re-patching** (line 1537): genMods 1540, genFx 1592, fxDesc 1620, destRange 1629, destName 1641, srcDesc 1642, create 1652, makeIR 1659, curve 1672, initGraph 1673, gateStep 1704, prepWaves 1706, applyFx 1713, mixVal 1735, applyMix 1736, loopD 1738, airNorm 1739, foldCurve 1740, bitCurve 1743, quantCurve 1744, chroma 1745, fxRotor 1752, fxBitplane 1760, fxHalo 1767, fxStrings 1785, fxShifter 1793, fxSonar 1807, buildFx 1817, retireFx 1825, globalParams 1829, buildMods 1830, retireMods 1851, modTick 1857, envMul 1893, ampOf 1894, Voice 1897
- **voices** (line 2012): polyOn 2014, polyOff 2019, mono 2020, playRec 2026, playPhrase 2030, releaseAll 2033
- **script starts** (line 2099): (no functions)
- **ENGINE** (line 2125): isMan 2151, kickOn 2152, kickHeld 2153, rnd 2326, euclid 2331, charOf 2336, genSteps 2337, varWeight 2364, mutateSteps 2365, mutateStepsX 2366, variant 2400, anySolo 2405, fillOn 2407, condOk 2409, dlgPalette 2424, dlgPlan 2426, lifeInfo 2450, eventsAt 2457, stepDur 2488, grooveOff 2492, hitsOf 2502, midiNote 2507, mname 2515, inScale 2516, snap 2517, nearestPC 2518
- **STATE** (line 2521): panMig 2527, freshLane 2531, lanesFrom 2538, oOpen 2548, migrateFx 2552, migrateSnap 2555, invalidate 2574, polyLen 2577, regen 2587, regenAll 2592, applyPreset 2593, varyLane 2611, metric 2627, contextOcc 2628, randLane 2635, hasHits 2672, anchorIds 2676, lhlW 2678, syncOf 2680, patternFeatures 2687, sugTargets 2702, scorePattern 2709, hamming 2719, currentPat 2720, makeSuggestions 2721, applySuggestion 2739, hSnap 2747, hApply 2748, hRecord 2749, hStep 2754, favSnap 2756, favLoad 2758, resetBasis 2765, tuneToKey 2771, resetKit 2773, rollKit 2774, rollLane 2779, patternData 2790, kitData 2791, applyPattern 2792, applyKit 2800
- **AUDIO** (line 2812): noiseBuf 2828, env 2829, noise 2830, mtof 2831, bq 2832, tone 2833, cents 2841, vMem 2843, vBell 2875, pulseBuf 2905, vUdu 2911, vTri 2928, vTabla 2947, vBayan 2964, vWood 2974, vTamb 2986, vClap 3006, vShk 3017, driftAt 3028, chokeIn 3036, voice 3040, voiceKind 3052, vcSpec 3074, vcGet 3081, vcPump 3084
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3094): irKey 3105, makeIR 3106, springIR 3133, unityCurve 3145, satCurve 3146, buildReverb 3147, bloomOn 3159, bloomHz 3160, bloomSync 3161, bloomStep 3164, buildDelay 3165, tapeCurve 3194, NgomaFilterCore 3198, NgomaFilterProc 3266, NgomaRecProc 3279, NgomaCombProc 3287, NgomaShimProc 3301, loadFilter 3316, attachFilter 3324, smooth 3343, mgDecK 3345, mgP 3346, buildMagic 3347, presetTrim 3383, magicSync 3384, magicWorklet 3396, combFallback 3402, resChord 3412, resMsg 3421, resStep 3423, resHz 3425, procSync 3426, combStep 3438, formantStep 3444, glitchStep 3449, cosmosErase 3463, padNotes 3473, padRoot 3482, padLoops 3483, softTone 3492, padSc 3505, padNt 3506, chProgOf 3516, chOn 3517, chPer 3518, chSemi 3519, chDegOf 3520, chWander 3522, chordAt 3527, chName 3529, chKey 3531, chTn 3536, chLabel 3542, tideState 3548, padTides 3560, tideTone 3565, echoPhrase 3574, padEchoes 3580, echoTone 3587, seasonChord 3598, seasonHold 3611, padSeasons 3612, warmVoice 3621, subVoice 3628, grain 3631, padRare 3637, buildPad 3645, padCutHz 3660, unitFlt 3664, fltHz 3665, fltFmt 3666, unitWet 3667, unitEcho 3668, unitTr 3669, trDeg 3670, pmtof 3671, wTry 3674, padTy 3675, padLive 3676, padSync 3677, padDrone 3690, droneVoice 3692, worpSeed 3702, padRecOn 3707, stepNow 3708, nrecUI 3709, nrecToggle 3712, nrecStop 3719, nrecNote 3720, nrecTick 3723, padMine 3729, worpSpec 3730, worpCode 3731, worpFlt 3733, worpToken 3734
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3735): lineMine 3747, recOn 3748, midiConnect 3749, midiPadOK 3756, midiDest 3757, midiShort 3758, midiUI 3759, midiQT 3764, midiKey 3767, ngMidi 3769, midiAuto 3775, leadAnchorTpl 3777, leadAnchorFn 3780, leadGain 3782, leadMeasure 3783, buildDub 3793, dubSync 3798, fltQ 3802, buildLead 3803
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3809): fldTrim 3824, fldId 3825, fldInfo 3826, fldKey 3827, fldBuf 3828, fldNorm 3829, fldDecode 3831, fldLoad 3832, fldOwnLoad 3841, fldOwnSet 3843, buildField 3844, fldLive 3848, fldHz 3849, fldStopLoop 3850, fldSync 3851, fldWalk 3858, fldStep 3859, fldDuck 3871, fldUI 3872, leadLive 3876, leadSpec 3877, leadSync 3878, leadEngine 3880, leadBar 3890, lcdSet 3897, leadUI 3898, worpBar 3903, worpUI 3919, worpParse 3925, worpUse 3931, worpHash 3933, WBC 3936, ctxEpoch 3937, worpState 3939, worpPost 3942, worpMsg 3947, worpPanel 3972, padBar 3978, buildGraph 4004, buildRoom 4034, roomSync 4039, clipCurve 4041, vetOn 4043, vetAmt 4044, VET_TRIM 4045, masterCurve 4049, buildVet 4050, vetSync 4064, shaperCurve 4068, lfoHz 4070, lfoPeriod 4071, cutPos 4072, cutHz 4073, syncFx 4074, pv 4104, syncGraph 4105, animCurve 4111, animValues 4113, applyAnim 4115, animLive 4121, fxTail 4123, flamGuard 4136, mgQ 4141, scheduleStep 4142, evN 4168, hitGate 4169, AUD 4178, STABLE 4179, loadLate 4180, stableSet 4181, ensureCtx 4184, tick 4185, start 4190, stop 4192, setDrop 4198, setDrumsOff 4201, dropApply 4202, dropMask 4207, preview 4208, $ 4215, mvolGain 4217, setMvol 4218, initMvol 4222, flashLed 4228
- **First visit: invite to press Play, then one next step** (line 4234): onbSave 4237, hintShow 4238, hintHide 4239, onbInit 4240, onbPlayed 4242, onbActed 4243, setPlayUI 4245, clearNow 4246, showDrift 4247, magicGlow 4255
- **Scope: a quiet oscilloscope in the house colours** (line 4262): scopeInit 4266, scopeCalm 4270, scopeCols 4271, scopeHit 4272, scopeWake 4273, scopeGrid 4274, scopeTrace 4277, scopeIdle 4279, scopeFrame 4280, draw 4299, makeSegK 4330, makeSelK 4334, makeKnob 4338, editX 4364, kfoldSeen 4374, kfoldHint 4375, laneRow 4379, paintPending 4459, paintCell 4461, editCell 4477, euRow 4489, renderLanes 4504, renderStyles 4516, initTips 4545, initValues 4560, bindMacro 4561, initControls 4565, status 4872, afterLoad 4873, updHist 4874, renderFavs 4875, inflate 4886, loadShared 4887, fileBase 4892
- **EXPORT: WAV** (line 4897): wavBytes 4899, kCoefs 4911, loudness 4916, truePeak 4926, midiBytes 4932, midiBytesX 4933, chLen 4960, chordMidiBytes 4961, CRC 4968, crc32 4969, zipBlob 4970, loopLen 4990, renderLoop 4992, renderLoopX 4993
- **Capture: keep what you just heard** (line 5002): capAttach 5007, capStart 5015, capLog 5016, capWindow 5017, capAudio 5023, capMidi 5027, capture 5037
- **Delivery: a folder you picked (no zip), or a zip download** (line 5050): idb 5052, kvSet 5053, kvGet 5054, outUI 5055, outPick 5056, outReady 5057, writeFiles 5058, deliver 5060, resampleTo 5066
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5068): dwKey 5070, dwPrepare 5071
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5076): jamTrack 5083, jamPut 5084, jamRec 5086, jamStart 5088, jamWorp 5097, jamUI 5100, jamStop 5104, jamWav 5114, jamFiles 5119
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5126): bbUI 5130, bbPick 5131, bbName 5132, bbSend 5136, exportLoop 5156
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5197): m4lAlign 5200, m4lInit 5204
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5236): onBar 5240, qRun 5244, qMark 5246, qDraw 5249
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5254): scenesRender 5256, sceneStore 5267, sceneClear 5268, sceneRecall 5269
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5272): morphCap 5281, morphStart 5283, morphSet 5292, morphInd 5309, morphSnap 5311, scBase 5315, scEdited 5316, morphStep 5319, morphEnd 5321, morphUI 5329, setView 5341

## Worp: public/worp/index.html (1840 lines)

- **script starts** (line 445): $ 447, mtof 458, mod 459
- **seeded dice** (line 461): rng 462, scaleLabel 473, semis 474
- **patch generation: chance inside musical limits** (line 476): genSpectrum 477, fromHist 491, histEntry 492, genName 493, uniqueName 502, genPatch 503
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 611): anchorFrom 629, euclidW 631, genPhraseStyle 632, rnd01 671, phraseAt 674, phraseAt0 676, phCx 684, phZ 685, phraseCore 686, phraseDesc 721
- **the modular part: sources, cables, re-patching** (line 723): genMods 726, genFx 778, fxDesc 806, destRange 815, destName 827, srcDesc 828
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 837): NgomaFilterCore 840, NgomaFilterProc 908, WorpRecProc 919, cutHz 933, loadFilter 934, syncFilter 941, saveFilter 945, saveEnv 948
- **audio graph** (line 950): makeIR 952, curve 965, initAudio 966, gateStep 1003, prepWaves 1005, applyFx 1012, mixVal 1034, applyMix 1035, loopD 1037, airNorm 1038, foldCurve 1039, bitCurve 1042, quantCurve 1043, chroma 1044, fxRotor 1051, fxBitplane 1059, fxHalo 1066, fxStrings 1084, fxShifter 1092, fxSonar 1106, buildFx 1116, retireFx 1124, globalParams 1128, buildMods 1129, retireMods 1150, modTick 1156, envMul 1192, ampOf 1193, Voice 1196
- **voices** (line 1311): polyOn 1313, polyOff 1318, mono 1319, playRec 1325, playPhrase 1329, releaseAll 1332, liveOn 1338, liveOff 1348, setSustain 1361
- **state** (line 1363): cur 1365, getBpm 1366, newSeed 1367, load 1368, save 1369, setPatch 1371, roll 1386, back 1391, setMode 1395
- **playing by itself** (line 1409): startDrone 1411, evolveDrone 1412, tick 1420, startPlay 1431, stopPlay 1442
- **MIDI** (line 1449): midiStatus 1451, initMIDI 1452, onMidi 1460, renderLearn 1477
- **rendering** (line 1484): noteName 1485, layerDetail 1486, layerTag 1493
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1495): BC 1500, ngomaOpen 1501, linked 1506, outGain 1508, epochToCtx 1509, hostT0 1512, relock 1513, transportSync 1515, worpPost 1523, setPlayUI 1524, hostVoicing 1529, applyHost 1531, hostChanged 1533, renderFollow 1540, focusNgoma 1543, toNgoma 1547, onHostMsg 1548, recStart 1564, recStop 1568, patchCode 1573, fltTok 1576, shareToken 1577, setFLT 1578, setENV 1579, envTok 1580, envNeutral 1581, hearInNgoma 1587, renderLive 1590, parseToken 1593, render 1597, renderFx 1623, renderPatch 1629, renderMusic 1638, lineHas 1655, lineUI 1656, lineSet 1658, drawSteps 1662, recLine 1671, recQ 1679, recFinish 1680, kbStart 1690, buildKb 1691, markKey 1699, ptrUp 1703, togglePlay 1718
- **ring visual** (line 1728): ringAn 1732, draw 1733
- **wiring** (line 1757): renderFilter 1777, secT 1786, renderEnv 1787, fillRange 1833
