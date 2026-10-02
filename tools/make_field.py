#!/usr/bin/env python3
"""Ngoma Field: cut the downloaded recordings (field_src/, from tools/get_field.sh) into seamless loops in public/field/.
Per recording: high-pass 35 Hz (higher for wind rumble, see HP), find the calmest stretch (the steadiest loudness, no single event far above the rest), take 48 s,
crossfade its last 3 s into its start (equal power) so it loops without a seam, normalise to -20 dBFS RMS with peaks under -3 dBFS,
encode mp3 128 kbps (stereo, or mono when the source is mono). Run: python3 tools/make_field.py"""
import subprocess, numpy as np, os, sys, json
SR, LEN, XF = 48000, 48.0, 3.0
IDS = ['water', 'night', 'wires', 'dawn', 'ice', 'city', 'bats']
HP = {'ice': 160, 'wires': 110, 'bats': 60}   # wind rumble out where it hides what the recording is about
EV = {'city': 1.0}   # the dogs in the city recording: prefer the stretch with the fewest loud events
os.makedirs('public/field', exist_ok=True); rep = {}
for id in IDS:
    src = 'field_src/%s.mp3' % id
    if not os.path.exists(src): print('missing', src); continue
    ch = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=channels', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip() or 2)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-af', 'highpass=f=%d,highpass=f=%d' % (HP.get(id, 35), HP.get(id, 35)), '-ar', str(SR), '-ac', str(ch), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, ch).astype(np.float64)
    n, L, X = len(x), int(LEN * SR), int(XF * SR)
    if n < L + X: L = n - X - SR
    mono = x.mean(1); w = SR // 2; k = len(mono) // w
    db = 10 * np.log10(np.array([np.mean(mono[i*w:(i+1)*w]**2) for i in range(k)]) + 1e-12)
    pk = np.array([np.max(np.abs(mono[i*w:(i+1)*w])) for i in range(k)])
    span = L // w; best, bi = 1e9, 0
    for i in range(0, max(1, k - span - (X // w) - 1)):
        seg = db[i:i+span]; crest = 20*np.log10(pk[i:i+span].max()+1e-9) - 10*np.log10(np.mean(10**(seg/10))+1e-12)
        score = np.std(seg) + .25 * max(0, crest - 14) + .02 * max(0, -30 - np.mean(seg)) + EV.get(id, 0) * np.sum(seg > np.median(db) + 9)
        if score < best: best, bi = score, i
    s0 = bi * w; seg = x[s0:s0 + L + X].copy()
    t = np.linspace(0, np.pi / 2, X)[:, None]
    loop = seg[:L].copy(); loop[:X] = seg[:X] * np.sin(t) + seg[L:L+X] * np.cos(t)   # the end runs into the start
    r = np.sqrt(np.mean(loop**2)); loop *= 0.1 / max(r, 1e-6)
    p = np.max(np.abs(loop)); lim = 10**(-3/20)
    if p > lim: loop = np.tanh(loop / lim * .9) * lim / np.tanh(.9) if p > 2*lim else loop * (lim / p)
    out = 'public/field/%s.mp3' % id
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', str(ch), '-i', '-', '-c:a', 'libmp3lame', '-b:a', '128k' if ch > 1 else '96k', out], input=loop.astype(np.float32).tobytes(), check=True)
    import base64   # v169: the same mp3 wrapped in a script, so Ngoma also finds it when opened as a file (file://, Max for Live)
    open('public/field/%s.js' % id, 'w').write("(window.NGOMA_FIELD=window.NGOMA_FIELD||{})['%s']='%s';\n" % (id, base64.b64encode(open(out, 'rb').read()).decode()))
    rep[id] = {'from_s': round(s0 / SR, 1), 'len_s': round(L / SR, 1), 'ch': ch, 'score': round(best, 2), 'kb': os.path.getsize(out) // 1024}
    print(id, rep[id])
json.dump(rep, open('public/field/cuts.json', 'w'), indent=1)
