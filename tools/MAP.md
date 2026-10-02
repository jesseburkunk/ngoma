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

## Ngoma: public/index.html (5439 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1261): mtof 1276, mod 1277
- **seeded dice** (line 1279): rng 1280, scaleLabel 1291, semis 1292
- **patch generation: chance inside musical limits** (line 1294): genSpectrum 1295, fromHist 1309, histEntry 1310, genName 1311, uniqueName 1320, genPatch 1321
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1429): anchorFrom 1447, euclidW 1449, genPhraseStyle 1450, rnd01 1489, phraseAt 1492, phraseAt0 1494, phCx 1502, phZ 1503, phraseCore 1504, phraseDesc 1539, lvSd 1548, lvMem 1549, lvP2 1554, lvCt 1555, lvSnap 1556, lvBar 1557, phraseV2 1573, phraseOut 1581
- **the modular part: sources, cables, re-patching** (line 1583): genMods 1586, genFx 1638, fxDesc 1666, destRange 1675, destName 1687, srcDesc 1688, create 1698, makeIR 1705, curve 1718, initGraph 1719, gateStep 1750, prepWaves 1752, applyFx 1759, mixVal 1781, applyMix 1782, loopD 1784, airNorm 1785, foldCurve 1786, bitCurve 1789, quantCurve 1790, chroma 1791, fxRotor 1798, fxBitplane 1806, fxHalo 1813, fxStrings 1831, fxShifter 1839, fxSonar 1853, buildFx 1863, retireFx 1871, globalParams 1875, buildMods 1876, retireMods 1897, modTick 1903, envMul 1939, ampOf 1940, Voice 1943
- **voices** (line 2058): polyOn 2060, polyOff 2065, mono 2066, playRec 2072, playPhrase 2076, releaseAll 2079, lineAt 2142
- **script starts** (line 2146): (no functions)
- **ENGINE** (line 2172): isMan 2198, kickOn 2199, kickHeld 2200, rnd 2373, euclid 2378, charOf 2383, genSteps 2384, varWeight 2411, mutateSteps 2412, mutateStepsX 2413, variant 2447, anySolo 2452, fillOn 2454, condOk 2456, dlgPalette 2471, dlgPlan 2473, lifeInfo 2497, eventsAt 2504, stepDur 2535, grooveOff 2539, hitsOf 2549, midiNote 2554, mname 2562, inScale 2563, snap 2564, nearestPC 2565
- **STATE** (line 2568): panMig 2574, freshLane 2578, lanesFrom 2585, oOpen 2595, migrateFx 2599, migrateSnap 2602, invalidate 2621, polyLen 2624, regen 2634, regenAll 2639, applyPreset 2640, varyLane 2658, metric 2674, contextOcc 2675, randLane 2682, hasHits 2719, anchorIds 2723, lhlW 2725, syncOf 2727, patternFeatures 2734, sugTargets 2749, scorePattern 2756, hamming 2766, currentPat 2767, makeSuggestions 2768, applySuggestion 2786, hSnap 2794, hApply 2795, hRecord 2796, hStep 2801, favSnap 2803, favLoad 2805, resetBasis 2812, tuneToKey 2818, resetKit 2820, rollKit 2821, rollLane 2826, patternData 2837, kitData 2838, applyPattern 2839, applyKit 2847
- **AUDIO** (line 2859): noiseBuf 2875, env 2876, noise 2877, mtof 2878, bq 2879, tone 2880, cents 2888, vMem 2890, vBell 2922, pulseBuf 2952, vUdu 2958, vTri 2975, vTabla 2994, vBayan 3011, vWood 3021, vTamb 3033, vClap 3053, vShk 3064, driftAt 3075, chokeIn 3083, voice 3087, voiceKind 3099, vcSpec 3121, vcGet 3128, vcPump 3131
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3141): irKey 3152, makeIR 3153, springIR 3180, unityCurve 3192, satCurve 3193, buildReverb 3194, bloomOn 3206, bloomHz 3207, bloomSync 3208, bloomStep 3211, buildDelay 3212, tapeCurve 3241, NgomaFilterCore 3245, NgomaFilterProc 3313, NgomaRecProc 3326, NgomaCombProc 3334, NgomaShimProc 3348, loadFilter 3363, attachFilter 3371, smooth 3390, mgDecK 3392, mgP 3393, buildMagic 3394, presetTrim 3430, magicSync 3431, magicWorklet 3443, combFallback 3449, resChord 3459, resMsg 3468, resStep 3470, resHz 3472, procSync 3473, combStep 3485, formantStep 3491, glitchStep 3496, cosmosErase 3510, padNotes 3520, padRoot 3529, padLoops 3530, softTone 3539, padSc 3552, padNt 3553, chProgOf 3563, chOn 3564, chPer 3565, chSemi 3566, chDegOf 3567, chWander 3569, chordAt 3574, chName 3576, chKey 3578, chTn 3583, chLabel 3589, tideState 3595, padTides 3607, tideTone 3612, echoPhrase 3621, padEchoes 3627, echoTone 3634, seasonChord 3645, seasonHold 3658, padSeasons 3659, warmVoice 3668, subVoice 3675, grain 3678, padRare 3684, buildPad 3692, padCutHz 3707, unitFlt 3711, fltHz 3712, fltFmt 3713, unitWet 3714, unitEcho 3715, unitTr 3716, trDeg 3717, pmtof 3718, wTry 3721, padTy 3722, padLive 3723, padSync 3724, padDrone 3737, droneVoice 3739, worpSeed 3749, padRecOn 3754, stepNow 3755, nrecUI 3756, nrecClicks 3764, nrecToggle 3767, nrecStop 3774, nrecNote 3775, nrecTick 3778, padMine 3784, worpSpec 3785, worpCode 3786, worpFlt 3788, worpToken 3789
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3790): lineMine 3802, recOn 3803, midiConnect 3804, midiPadOK 3811, midiDest 3812, midiShort 3813, midiUI 3814, midiQT 3819, midiKey 3822, ngMidi 3824, midiAuto 3830, leadAnchorTpl 3832, leadAnchorFn 3835, leadLv 3841, leadDrum 3842, leadGain 3844, leadMeasure 3845, buildDub 3855, dubSync 3860, fltQ 3864, buildLead 3865
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3871): fldTrim 3886, fldId 3887, fldInfo 3888, fldKey 3889, fldBuf 3890, fldNorm 3891, fldDecode 3893, fldLoad 3894, fldOwnLoad 3903, fldOwnSet 3905, buildField 3906, fldLive 3910, fldHz 3911, fldStopLoop 3912, fldSync 3913, fldWalk 3920, fldStep 3921, fldDuck 3933, fldUI 3934, leadLive 3938, leadSpec 3939, leadSync 3940, leadEngine 3942, leadBar 3952, lcdSet 3959, leadUI 3960, worpBar 3965, worpUI 3981, worpParse 3987, worpUse 3993, worpHash 3995, WBC 3998, ctxEpoch 3999, worpState 4001, worpPost 4004, worpMsg 4009, worpPanel 4034, padBar 4040, buildGraph 4066, buildRoom 4096, roomSync 4101, clipCurve 4103, vetOn 4105, vetAmt 4106, VET_TRIM 4107, masterCurve 4111, buildVet 4112, vetSync 4126, shaperCurve 4130, lfoHz 4132, lfoPeriod 4133, cutPos 4134, cutHz 4135, syncFx 4136, pv 4166, syncGraph 4167, animCurve 4173, animValues 4175, applyAnim 4177, animLive 4183, fxTail 4185, flamGuard 4198, mgQ 4203, scheduleStep 4204, evN 4230, hitGate 4231, AUD 4240, STABLE 4241, loadLate 4242, stableSet 4243, ensureCtx 4246, tick 4247, start 4252, stop 4254, setDrop 4260, setDrumsOff 4263, dropApply 4264, dropMask 4269, preview 4270, $ 4277, mvolGain 4279, setMvol 4280, initMvol 4284, flashLed 4290
- **First visit: invite to press Play, then one next step** (line 4296): onbSave 4299, hintShow 4300, hintHide 4301, onbInit 4302, onbPlayed 4304, onbActed 4305, setPlayUI 4307, clearNow 4308, showDrift 4309, magicGlow 4317
- **Scope: a quiet oscilloscope in the house colours** (line 4324): scopeInit 4328, scopeCalm 4332, scopeCols 4333, scopeHit 4334, scopeWake 4335, scopeGrid 4336, scopeTrace 4339, scopeIdle 4341, scopeFrame 4342, draw 4361, makeSegK 4392, makeSelK 4396, makeKnob 4400, editX 4426, kfoldSeen 4436, kfoldHint 4437, laneRow 4441, paintPending 4521, paintCell 4523, editCell 4539, euRow 4551, renderLanes 4566, renderStyles 4578, initTips 4607, initValues 4622, bindMacro 4623, initControls 4627, status 4955, afterLoad 4956, updHist 4957, renderFavs 4958, inflate 4969, loadShared 4970, fileBase 4975
- **EXPORT: WAV** (line 4980): wavBytes 4982, kCoefs 4994, loudness 4999, truePeak 5009, midiBytes 5015, midiBytesX 5016, chLen 5043, chordMidiBytes 5044, CRC 5051, crc32 5052, zipBlob 5053, loopLen 5073, renderLoop 5075, renderLoopX 5076
- **Capture: keep what you just heard** (line 5085): capAttach 5090, capStart 5098, capLog 5099, capWindow 5100, capAudio 5106, capMidi 5110, capture 5120
- **Delivery: a folder you picked (no zip), or a zip download** (line 5133): idb 5135, kvSet 5136, kvGet 5137, outUI 5138, outPick 5139, outReady 5140, writeFiles 5141, deliver 5143, resampleTo 5149
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5151): dwKey 5153, dwPrepare 5154
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5159): jamTrack 5166, jamPut 5167, jamRec 5169, jamStart 5171, jamWorp 5180, jamUI 5183, jamStop 5187, jamWav 5197, jamFiles 5202
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5209): bbUI 5213, bbPick 5214, bbName 5215, bbSend 5219, exportLoop 5239
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5280): m4lAlign 5283, m4lInit 5287
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5319): onBar 5323, qRun 5327, qMark 5329, qDraw 5332
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5337): scenesRender 5339, sceneStore 5350, sceneClear 5351, sceneRecall 5352
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5355): morphCap 5364, morphStart 5366, morphSet 5375, morphInd 5392, morphSnap 5394, scBase 5398, scEdited 5399, morphStep 5402, morphEnd 5404, morphUI 5412, setView 5424

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
