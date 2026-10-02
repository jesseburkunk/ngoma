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

## Ngoma: public/index.html (5607 lines)

- **script starts** (line 13): (no functions)
- **Knobs with character (v71): a ribbed skirt that turns (after the Rogan knobs of the Prophe** (line 431): (no functions)
- **Origins (v78): its own dialog, first button in the top bar** (line 456): (no functions)
- **Transport in groups (v94): play, time, tuning, mix** (line 474): (no functions)
- **Sticky mini transport (v94): appears when the main transport scrolls away** (line 484): (no functions)
- **Scenes (v91)** (line 496): (no functions)
- **Changes on the next bar (v88)** (line 522): (no functions)
- **Simple view (v76): same engine, fewer controls. Nothing is reset; Full shows everything ag** (line 532): (no functions)
- **script starts** (line 1298): mtof 1313, mod 1314
- **seeded dice** (line 1316): rng 1317, scaleLabel 1328, semis 1329
- **patch generation: chance inside musical limits** (line 1331): genSpectrum 1332, fromHist 1346, histEntry 1347, genName 1348, uniqueName 1357, genPatch 1358
- **lead phrases (v1.3, v1.9, v1.12): nine ways to make a line, after minimalist practice. Eve** (line 1481): anchorFrom 1499, euclidW 1501, genPhraseStyle 1502, rnd01 1541, phraseAt 1544, phraseAt0 1546, phCx 1554, phZ 1555, phraseCore 1556, phraseDesc 1591, lvSd 1600, lvMem 1601, lvP2 1606, lvCt 1607, lvSnap 1608, lvBar 1609, phraseV2 1625, phraseOut 1633
- **the modular part: sources, cables, re-patching** (line 1635): genMods 1638, genFx 1690, fxDesc 1718, destRange 1727, destName 1739, srcDesc 1740, create 1750, makeIR 1757, curve 1770, initGraph 1771, gateStep 1802, prepWaves 1804, applyFx 1811, mixVal 1833, applyMix 1834, loopD 1836, airNorm 1837, foldCurve 1838, bitCurve 1841, quantCurve 1842, chroma 1843, fxRotor 1850, fxBitplane 1858, fxHalo 1865, fxStrings 1883, fxShifter 1891, fxSonar 1905, buildFx 1915, retireFx 1923, globalParams 1927, buildMods 1928, retireMods 1949, modTick 1955, envMul 1991, ampOf 1992, Voice 1995
- **voices** (line 2110): polyOn 2112, polyOff 2117, mono 2118, playRec 2124, playPhrase 2128, releaseAll 2131, lineAt 2194, setHostScale 2195
- **script starts** (line 2199): (no functions)
- **ENGINE** (line 2225): isMan 2251, kickOn 2252, kickHeld 2253, rnd 2426, euclid 2431, charOf 2436, genSteps 2437, varWeight 2464, mutateSteps 2465, mutateStepsX 2466, variant 2500, anySolo 2505, fillOn 2507, condOk 2509, dlgPalette 2524, dlgPlan 2526, lifeInfo 2550, eventsAt 2557, stepDur 2588, grooveOff 2592, hitsOf 2602, midiNote 2607, mname 2615, inScale 2616, snap 2617, nearestPC 2618
- **STATE** (line 2621): panMig 2627, freshLane 2631, lanesFrom 2638, oOpen 2648, migrateFx 2652, migrateSnap 2655, invalidate 2674, polyLen 2677, regen 2687, regenAll 2692, applyPreset 2693, varyLane 2711, metric 2727, contextOcc 2728, randLane 2735, hasHits 2772, anchorIds 2776, lhlW 2778, syncOf 2780, patternFeatures 2787, sugTargets 2802, scorePattern 2809, hamming 2819, currentPat 2820, makeSuggestions 2821, applySuggestion 2839, hSnap 2847, hApply 2848, hRecord 2849, hStep 2854, favSnap 2856, favLoad 2858, resetBasis 2865, tuneToKey 2871, resetKit 2873, rollKit 2874, rollLane 2879, patternData 2890, kitData 2891, applyPattern 2892, applyKit 2900
- **AUDIO** (line 2912): noiseBuf 2928, env 2929, noise 2930, mtof 2931, bq 2932, tone 2933, cents 2941, vMem 2943, vBell 2975, pulseBuf 3005, vUdu 3011, vTri 3028, vTabla 3047, vBayan 3064, vWood 3074, vTamb 3086, vClap 3106, vShk 3117, driftAt 3128, chokeIn 3136, voice 3140, voiceKind 3152, vcSpec 3174, vcGet 3181, vcPump 3184
- **Space: reverb (algorithmic impulse response) and tape-style delay** (line 3194): irKey 3205, makeIR 3206, springIR 3233, unityCurve 3245, satCurve 3246, buildReverb 3247, bloomOn 3259, bloomHz 3260, bloomSync 3261, bloomStep 3264, buildDelay 3265, tapeCurve 3294, NgomaFilterCore 3298, NgomaFilterProc 3366, NgomaRecProc 3379, NgomaCombProc 3387, NgomaShimProc 3401, NgomaPlaitsProc 3412, loadFilter 3439, attachFilter 3447, smooth 3466, mgDecK 3468, mgP 3469, buildMagic 3470, presetTrim 3506, magicSync 3507, magicWorklet 3519, combFallback 3525, resChord 3535, resMsg 3544, resStep 3546, resHz 3548, procSync 3549, combStep 3561, formantStep 3567, glitchStep 3572, cosmosErase 3586, padNotes 3596, padRoot 3605, padLoops 3606, softTone 3615, padSc 3628, padNt 3629, chProgOf 3639, chOn 3640, chPer 3641, chSemi 3642, chDegOf 3643, chWander 3645, chordAt 3650, chName 3652, chKey 3654, chTn 3659, chLabel 3665, tideState 3671, padTides 3683, tideTone 3688, echoPhrase 3697, padEchoes 3703, echoTone 3710, seasonChord 3721, seasonHold 3734, padSeasons 3735, warmVoice 3744, subVoice 3751, grain 3754, padRare 3760, buildPad 3768, padCutHz 3783, unitFlt 3787, fltHz 3788, fltFmt 3789, unitWet 3790, unitEcho 3791, unitTr 3792, trDeg 3793, pmtof 3794, wTry 3797, padTy 3798, padLive 3799, padSync 3800, padDrone 3813, droneVoice 3815, worpSeed 3825, padRecOn 3830, stepNow 3831, nrecUI 3832, nrecClicks 3840, nrecToggle 3843, nrecStop 3850, nrecNote 3851, nrecTick 3854, padMine 3860, worpSpec 3861, worpCode 3862, worpFlt 3864, worpToken 3865
- **Lead (v106): a Worp lead as its own unit. One voice with glide plays the patch's phrase in** (line 3866): lineMine 3878, recOn 3879, midiConnect 3880, midiPadOK 3887, midiDest 3888, midiShort 3889, midiUI 3890, midiQT 3895, midiKey 3898, ngMidi 3900, midiAuto 3906, leadAnchorTpl 3908, leadAnchorFn 3911, leadLv 3917, leadDrum 3918, plPatch 3928, plMove 3934, plBytes 3939, plEngine 3940, plSync 3943, plNote 3945, plKeys 3947, plPhrase 3950, plSemi 3951, plRec 3953, plBar 3955, leadGain 3961, buildDub 3965, dubSync 3970, fltQ 3974, buildLead 3975
- **Field (v168; Jesse: a layer of field recordings, open material, in the spirit of Chris Wat** (line 3981): fldTrim 3996, fldId 3997, fldInfo 3998, fldKey 3999, fldBuf 4000, fldNorm 4001, fldDecode 4003, fldLoad 4004, fldOwnLoad 4013, fldOwnSet 4015, buildField 4016, fldLive 4020, fldHz 4021, fldStopLoop 4022, fldSync 4023, fldWalk 4030, fldStep 4031, fldDuck 4043, fldUI 4044
- **Candy (v180; Jesse: ear candy instead of a big texture: small sounds without a key that ma** (line 4048): buildCandy 4053, cdLive 4054, cdSeed 4055, cdSrc 4056, cdFid 4057, cdBuf 4058, cdSync 4059, cdPalette 4063, cdHit 4068, cdStep 4077, cdUI 4084, leadLive 4086, leadSpec 4087, leadSync 4088, leadBar 4090, lcdSet 4093, leadUI 4094, worpBar 4098, worpUI 4114, worpParse 4120, worpUse 4126, worpHash 4128, WBC 4131, ctxEpoch 4132, worpState 4134, worpPost 4137, worpMsg 4142, worpPanel 4161, padBar 4167, buildGraph 4193, buildRoom 4223, roomSync 4228, clipCurve 4230, vetOn 4232, vetAmt 4233, VET_TRIM 4234, masterCurve 4238, buildVet 4239, vetSync 4253, shaperCurve 4257, lfoHz 4259, lfoPeriod 4260, cutPos 4261, cutHz 4262, syncFx 4263, pv 4293, syncGraph 4294, animCurve 4300, animValues 4302, applyAnim 4304, animLive 4310, fxTail 4312, flamGuard 4325, mgQ 4330, scheduleStep 4331, evN 4357, hitGate 4358, AUD 4367, STABLE 4368, loadLate 4369, stableSet 4370, ensureCtx 4373, tick 4374, start 4379, stop 4381, setDrop 4386, setDrumsOff 4389, dropApply 4390, dropMask 4395, preview 4396, $ 4403, mvolGain 4405, setMvol 4406, initMvol 4410, flashLed 4416
- **First visit: invite to press Play, then one next step** (line 4422): onbSave 4425, hintShow 4426, hintHide 4427, onbInit 4428, onbPlayed 4430, onbActed 4431, setPlayUI 4433, clearNow 4434, showDrift 4435, magicGlow 4443
- **Scope: a quiet oscilloscope in the house colours** (line 4450): scopeInit 4454, scopeCalm 4458, scopeCols 4459, scopeHit 4460, scopeWake 4461, scopeGrid 4462, scopeTrace 4465, scopeIdle 4467, scopeFrame 4468, draw 4487, makeSegK 4518, makeSelK 4522, makeKnob 4526, editX 4552, kfoldSeen 4562, kfoldHint 4563, laneRow 4567, paintPending 4647, paintCell 4649, editCell 4665, euRow 4677, renderLanes 4692, renderStyles 4704, initTips 4733, initValues 4748, bindMacro 4749, layersLayout 4756, initControls 4771, status 5122, afterLoad 5123, updHist 5124, renderFavs 5125, inflate 5136, loadShared 5137, fileBase 5142
- **EXPORT: WAV** (line 5147): wavBytes 5149, kCoefs 5161, loudness 5166, truePeak 5176, midiBytes 5182, midiBytesX 5183, chLen 5210, chordMidiBytes 5211, CRC 5218, crc32 5219, zipBlob 5220, loopLen 5240, renderLoop 5242, renderLoopX 5243
- **Capture: keep what you just heard** (line 5252): capAttach 5257, capStart 5265, capLog 5266, capWindow 5267, capAudio 5273, capMidi 5277, capture 5287
- **Delivery: a folder you picked (no zip), or a zip download** (line 5300): idb 5302, kvSet 5303, kvGet 5304, outUI 5305, outPick 5306, outReady 5307, writeFiles 5308, deliver 5310, resampleTo 5316
- **Drag WAV: the mix is rendered while you hover, so it is ready when you drag** (line 5318): dwKey 5320, dwPrepare 5321
- **Jam recording (v101): press ● Rec, play for up to 12 minutes, press again. It starts on th** (line 5326): jamTrack 5333, jamPut 5334, jamRec 5336, jamStart 5338, jamWorp 5347, jamUI 5350, jamStop 5354, jamWav 5364, jamFiles 5369
- **Blackbox (v95): its own folder and names made for a small screen. Tempo (three digits, so ** (line 5376): bbUI 5380, bbPick 5381, bbName 5382, bbSend 5386, exportLoop 5406
- **Max for Live bridge (v77). Inside the Ngoma device (jweb~ in Live) Live's transport drives** (line 5447): m4lAlign 5450, m4lInit 5454
- **Changes on the next bar (v88). While playing, a new rhythm, Surprise, Reset, New variant, ** (line 5486): onBar 5490, qRun 5494, qMark 5496, qDraw 5499
- **Scenes (v91): eight slots that keep the whole state (the same snapshot as ← →: pattern, ki** (line 5504): scenesRender 5506, sceneStore 5517, sceneClear 5518, sceneRecall 5519
- **Morph (v104): a scene grows out of what plays now over 1, 2, 4 or 8 bars. The scene is app** (line 5522): morphCap 5531, morphStart 5533, morphSet 5542, morphInd 5559, morphSnap 5561, scBase 5565, scEdited 5566, morphStep 5569, morphEnd 5571, morphUI 5579, setView 5591
- **script starts** (line 5604): (no functions)

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
