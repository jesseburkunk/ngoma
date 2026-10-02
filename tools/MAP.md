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

## Ngoma: public/index.html (5407 lines)

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
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1425): anchorFrom 1443, euclidW 1445, genPhraseStyle 1446, rnd01 1485, phraseAt 1488, phraseAt0 1490, phCx 1498, phZ 1499, phraseCore 1500, phraseDesc 1535, lvSd 1544, lvMem 1545, lvP2 1550, lvCt 1551, lvSnap 1552, lvBar 1553, phraseV2 1569, phraseOut 1577
- **the modular part: sources, cables, re-patching** (line 1579): genMods 1582, genFx 1634, fxDesc 1662, destRange 1671, destName 1683, srcDesc 1684, create 1694, makeIR 1701, curve 1714, initGraph 1715, gateStep 1746, prepWaves 1748, applyFx 1755, mixVal 1777, applyMix 1778, loopD 1780, airNorm 1781, foldCurve 1782, bitCurve 1785, quantCurve 1786, chroma 1787, fxRotor 1794, fxBitplane 1802, fxHalo 1809, fxStrings 1827, fxShifter 1835, fxSonar 1849, buildFx 1859, retireFx 1867, globalParams 1871, buildMods 1872, retireMods 1893, modTick 1899, envMul 1935, ampOf 1936, Voice 1939
- **voices** (line 2054): polyOn 2056, polyOff 2061, mono 2062, playRec 2068, playPhrase 2072, releaseAll 2075, lineAt 2138
- **script starts** (line 2142): (no functions)
- **ENGINE** (line 2168): isMan 2194, kickOn 2195, kickHeld 2196, rnd 2369, euclid 2374, charOf 2379, genSteps 2380, varWeight 2407, mutateSteps 2408, mutateStepsX 2409, variant 2443, anySolo 2448, fillOn 2450, condOk 2452, dlgPalette 2467, dlgPlan 2469, lifeInfo 2493, eventsAt 2500, stepDur 2531, grooveOff 2535, hitsOf 2545, midiNote 2550, mname 2558, inScale 2559, snap 2560, nearestPC 2561
- **STATE** (line 2564): panMig 2570, freshLane 2574, lanesFrom 2581, oOpen 2591, migrateFx 2595, migrateSnap 2598, invalidate 2617, polyLen 2620, regen 2630, regenAll 2635, applyPreset 2636, varyLane 2654, metric 2670, contextOcc 2671, randLane 2678, hasHits 2715, anchorIds 2719, lhlW 2721, syncOf 2723, patternFeatures 2730, sugTargets 2745, scorePattern 2752, hamming 2762, currentPat 2763, makeSuggestions 2764, applySuggestion 2782, hSnap 2790, hApply 2791, hRecord 2792, hStep 2797, favSnap 2799, favLoad 2801, resetBasis 2808, tuneToKey 2814, resetKit 2816, rollKit 2817, rollLane 2822, patternData 2833, kitData 2834, applyPattern 2835, applyKit 2843
- **AUDIO** (line 2855): noiseBuf 2871, env 2872, noise 2873, mtof 2874, bq 2875, tone 2876, cents 2884, vMem 2886, vBell 2918, pulseBuf 2948, vUdu 2954, vTri 2971, vTabla 2990, vBayan 3007, vWood 3017, vTamb 3029, vClap 3049, vShk 3060, driftAt 3071, chokeIn 3079, voice 3083, voiceKind 3095, vcSpec 3117, vcGet 3124, vcPump 3127
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3137): irKey 3148, makeIR 3149, springIR 3176, unityCurve 3188, satCurve 3189, buildReverb 3190, bloomOn 3202, bloomHz 3203, bloomSync 3204, bloomStep 3207, buildDelay 3208, tapeCurve 3237, NgomaFilterCore 3241, NgomaFilterProc 3309, NgomaRecProc 3322, NgomaCombProc 3330, NgomaShimProc 3344, loadFilter 3359, attachFilter 3367, smooth 3386, mgDecK 3388, mgP 3389, buildMagic 3390, presetTrim 3426, magicSync 3427, magicWorklet 3439, combFallback 3445, resChord 3455, resMsg 3464, resStep 3466, resHz 3468, procSync 3469, combStep 3481, formantStep 3487, glitchStep 3492, cosmosErase 3506, padNotes 3516, padRoot 3525, padLoops 3526, softTone 3535, padSc 3548, padNt 3549, chProgOf 3559, chOn 3560, chPer 3561, chSemi 3562, chDegOf 3563, chWander 3565, chordAt 3570, chName 3572, chKey 3574, chTn 3579, chLabel 3585, tideState 3591, padTides 3603, tideTone 3608, echoPhrase 3617, padEchoes 3623, echoTone 3630, seasonChord 3641, seasonHold 3654, padSeasons 3655, warmVoice 3664, subVoice 3671, grain 3674, padRare 3680, buildPad 3688, padCutHz 3703, unitFlt 3707, fltHz 3708, fltFmt 3709, unitWet 3710, unitEcho 3711, unitTr 3712, trDeg 3713, pmtof 3714, wTry 3717, padTy 3718, padLive 3719, padSync 3720, padDrone 3733, droneVoice 3735, worpSeed 3745, padRecOn 3750, stepNow 3751, nrecUI 3752, nrecClicks 3760, nrecToggle 3763, nrecStop 3770, nrecNote 3771, nrecTick 3774, padMine 3780, worpSpec 3781, worpCode 3782, worpFlt 3784, worpToken 3785
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3786): lineMine 3798, recOn 3799, midiConnect 3800, midiPadOK 3807, midiDest 3808, midiShort 3809, midiUI 3810, midiQT 3815, midiKey 3818, ngMidi 3820, midiAuto 3826, leadAnchorTpl 3828, leadAnchorFn 3831, leadGain 3833, leadMeasure 3834, buildDub 3844, dubSync 3849, fltQ 3853, buildLead 3854
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3860): fldTrim 3875, fldId 3876, fldInfo 3877, fldKey 3878, fldBuf 3879, fldNorm 3880, fldDecode 3882, fldLoad 3883, fldOwnLoad 3892, fldOwnSet 3894, buildField 3895, fldLive 3899, fldHz 3900, fldStopLoop 3901, fldSync 3902, fldWalk 3909, fldStep 3910, fldDuck 3922, fldUI 3923, leadLive 3927, leadSpec 3928, leadSync 3929, leadEngine 3931, leadBar 3941, lcdSet 3948, leadUI 3949, worpBar 3954, worpUI 3970, worpParse 3976, worpUse 3982, worpHash 3984, WBC 3987, ctxEpoch 3988, worpState 3990, worpPost 3993, worpMsg 3998, worpPanel 4023, padBar 4029, buildGraph 4055, buildRoom 4085, roomSync 4090, clipCurve 4092, vetOn 4094, vetAmt 4095, VET_TRIM 4096, masterCurve 4100, buildVet 4101, vetSync 4115, shaperCurve 4119, lfoHz 4121, lfoPeriod 4122, cutPos 4123, cutHz 4124, syncFx 4125, pv 4155, syncGraph 4156, animCurve 4162, animValues 4164, applyAnim 4166, animLive 4172, fxTail 4174, flamGuard 4187, mgQ 4192, scheduleStep 4193, evN 4219, hitGate 4220, AUD 4229, STABLE 4230, loadLate 4231, stableSet 4232, ensureCtx 4235, tick 4236, start 4241, stop 4243, setDrop 4249, setDrumsOff 4252, dropApply 4253, dropMask 4258, preview 4259, $ 4266, mvolGain 4268, setMvol 4269, initMvol 4273, flashLed 4279
- **First visit: invite to press Play, then one next step** (line 4285): onbSave 4288, hintShow 4289, hintHide 4290, onbInit 4291, onbPlayed 4293, onbActed 4294, setPlayUI 4296, clearNow 4297, showDrift 4298, magicGlow 4306
- **Scope: a quiet oscilloscope in the house colours** (line 4313): scopeInit 4317, scopeCalm 4321, scopeCols 4322, scopeHit 4323, scopeWake 4324, scopeGrid 4325, scopeTrace 4328, scopeIdle 4330, scopeFrame 4331, draw 4350, makeSegK 4381, makeSelK 4385, makeKnob 4389, editX 4415, kfoldSeen 4425, kfoldHint 4426, laneRow 4430, paintPending 4510, paintCell 4512, editCell 4528, euRow 4540, renderLanes 4555, renderStyles 4567, initTips 4596, initValues 4611, bindMacro 4612, initControls 4616, status 4923, afterLoad 4924, updHist 4925, renderFavs 4926, inflate 4937, loadShared 4938, fileBase 4943
- **EXPORT: WAV** (line 4948): wavBytes 4950, kCoefs 4962, loudness 4967, truePeak 4977, midiBytes 4983, midiBytesX 4984, chLen 5011, chordMidiBytes 5012, CRC 5019, crc32 5020, zipBlob 5021, loopLen 5041, renderLoop 5043, renderLoopX 5044
- **Capture: keep what you just heard** (line 5053): capAttach 5058, capStart 5066, capLog 5067, capWindow 5068, capAudio 5074, capMidi 5078, capture 5088
- **Delivery: a folder you picked (no zip), or a zip download** (line 5101): idb 5103, kvSet 5104, kvGet 5105, outUI 5106, outPick 5107, outReady 5108, writeFiles 5109, deliver 5111, resampleTo 5117
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5119): dwKey 5121, dwPrepare 5122
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5127): jamTrack 5134, jamPut 5135, jamRec 5137, jamStart 5139, jamWorp 5148, jamUI 5151, jamStop 5155, jamWav 5165, jamFiles 5170
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5177): bbUI 5181, bbPick 5182, bbName 5183, bbSend 5187, exportLoop 5207
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5248): m4lAlign 5251, m4lInit 5255
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5287): onBar 5291, qRun 5295, qMark 5297, qDraw 5300
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5305): scenesRender 5307, sceneStore 5318, sceneClear 5319, sceneRecall 5320
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5323): morphCap 5332, morphStart 5334, morphSet 5343, morphInd 5360, morphSnap 5362, scBase 5366, scEdited 5367, morphStep 5370, morphEnd 5372, morphUI 5380, setView 5392

## Worp: public/worp/index.html (1882 lines)

- **script starts** (line 445): $ 447, mtof 458, mod 459
- **seeded dice** (line 461): rng 462, scaleLabel 473, semis 474
- **patch generation: chance inside musical limits** (line 476): genSpectrum 477, fromHist 491, histEntry 492, genName 493, uniqueName 502, genPatch 503
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 611): anchorFrom 629, euclidW 631, genPhraseStyle 632, rnd01 671, phraseAt 674, phraseAt0 676, phCx 684, phZ 685, phraseCore 686, phraseDesc 721, lvSd 730, lvMem 731, lvP2 736, lvCt 737, lvSnap 738, lvBar 739, phraseV2 755, phraseOut 763
- **the modular part: sources, cables, re-patching** (line 765): genMods 768, genFx 820, fxDesc 848, destRange 857, destName 869, srcDesc 870
- **master filter: the same four models as Ngoma (TPT/ZDF, 2x oversampled, in an AudioWorklet)** (line 879): NgomaFilterCore 882, NgomaFilterProc 950, WorpRecProc 961, cutHz 975, loadFilter 976, syncFilter 983, saveFilter 987, saveEnv 990
- **audio graph** (line 992): makeIR 994, curve 1007, initAudio 1008, gateStep 1045, prepWaves 1047, applyFx 1054, mixVal 1076, applyMix 1077, loopD 1079, airNorm 1080, foldCurve 1081, bitCurve 1084, quantCurve 1085, chroma 1086, fxRotor 1093, fxBitplane 1101, fxHalo 1108, fxStrings 1126, fxShifter 1134, fxSonar 1148, buildFx 1158, retireFx 1166, globalParams 1170, buildMods 1171, retireMods 1192, modTick 1198, envMul 1234, ampOf 1235, Voice 1238
- **voices** (line 1353): polyOn 1355, polyOff 1360, mono 1361, playRec 1367, playPhrase 1371, releaseAll 1374, liveOn 1380, liveOff 1390, setSustain 1403
- **state** (line 1405): cur 1407, getBpm 1408, newSeed 1409, load 1410, save 1411, setPatch 1413, roll 1428, back 1433, setMode 1437
- **playing by itself** (line 1451): startDrone 1453, evolveDrone 1454, tick 1462, startPlay 1473, stopPlay 1484
- **MIDI** (line 1491): midiStatus 1493, initMIDI 1494, onMidi 1502, renderLearn 1519
- **rendering** (line 1526): noteName 1527, layerDetail 1528, layerTag 1535
- **Ngoma next door: same site, so the two tabs talk over a BroadcastChannel** (line 1537): BC 1542, ngomaOpen 1543, linked 1548, outGain 1550, epochToCtx 1551, hostT0 1554, relock 1555, transportSync 1557, worpPost 1565, setPlayUI 1566, hostVoicing 1571, applyHost 1573, hostChanged 1575, renderFollow 1582, focusNgoma 1585, toNgoma 1589, onHostMsg 1590, recStart 1606, recStop 1610, patchCode 1615, fltTok 1618, shareToken 1619, setFLT 1620, setENV 1621, envTok 1622, envNeutral 1623, hearInNgoma 1629, renderLive 1632, parseToken 1635, render 1639, renderFx 1665, renderPatch 1671, renderMusic 1680, lineHas 1697, lineUI 1698, lineSet 1700, drawSteps 1704, recLine 1713, recQ 1721, recFinish 1722, kbStart 1732, buildKb 1733, markKey 1741, ptrUp 1745, togglePlay 1760
- **ring visual** (line 1770): ringAn 1774, draw 1775
- **wiring** (line 1799): renderFilter 1819, secT 1828, renderEnv 1829, fillRange 1875
