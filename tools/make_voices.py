#!/usr/bin/env python3
"""Ngoma Texture 'Voices' (v199): radio voices from NASA mission audio (Artemis II, public domain; field_src/voices/, saved by hand
from nasa.gov/artemisaudio). Per file: high-pass 120 Hz, low-pass 7 kHz, light FFT denoise, then find the spoken phrases (energy
above the file's own noise floor, short gaps bridged), keep the cleanest 0.7 to 4.5 s ones, level them to the same loudness and lay
them out with seeded pauses into one 48 s mono loop (the last second runs into the start). Run: python3 tools/make_voices.py [--list]"""
import subprocess, numpy as np, os, sys, json, glob, base64
SR, LEN, XF, FR = 48000, 48.0, 1.0, 960   # 20 ms frames
rng = np.random.default_rng(1969)
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', 'highpass=f=120,highpass=f=120,lowpass=f=7000,afftdn=nr=10:nf=-45', '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
segs = []
for f in sorted(glob.glob('field_src/voices/*')):
    x = load(f); k = len(x) // FR
    db = 10 * np.log10(np.array([np.mean(x[i*FR:(i+1)*FR]**2) for i in range(k)]) + 1e-12)
    floor = np.percentile(db, 15); on = (db > floor + 14) & (db > -52)
    # bridge gaps under 300 ms, drop blips under 300 ms
    i = 0; runs = []
    while i < k:
        if on[i]:
            j = i
            while j < k and (on[j] or (j + 15 < k and on[j:j+15].any())): j += 1
            runs.append((i, j)); i = j
        else: i += 1
    for a, b in runs:
        d = (b - a) * FR / SR
        if d < .7: continue
        if d > 4.5:   # cut at the quietest frame between 2.5 and 4.5 s
            lo, hi = a + int(2.5 * SR / FR), a + int(4.5 * SR / FR); b = lo + int(np.argmin(db[lo:hi])); d = (b - a) * FR / SR
        snr = float(np.mean(db[a:b]) - floor)
        segs.append({'f': os.path.basename(f), 'a': a * FR, 'b': b * FR, 'd': d, 'snr': snr, 'x': x})
if '--list' in sys.argv:
    for s in segs: print('%-55s %6.1f s  %4.1f s  snr %4.1f' % (s['f'], s['a'] / SR, s['d'], s['snr']))
    sys.exit()
# the cleanest phrases, at most 3 per file, until about 32 s of speech
segs.sort(key=lambda s: -s['snr']); pick, per, tot = [], {}, 0
for s in segs:
    if per.get(s['f'], 0) >= 3 or tot + s['d'] > 32: continue
    pick.append(s); per[s['f']] = per.get(s['f'], 0) + 1; tot += s['d']
rng.shuffle(pick)
L = int(LEN * SR); out = np.zeros(L + int(XF * SR)); pos = int(.6 * SR); used = []
gap = (LEN - tot - .6) / max(1, len(pick))
for s in pick:
    y = s['x'][s['a']:s['b']].copy(); fd = int(.015 * SR); y[:fd] *= np.linspace(0, 1, fd); y[-fd:] *= np.linspace(1, 0, fd)
    y *= .1 / max(np.sqrt(np.mean(y**2)), 1e-6)
    if pos + len(y) > len(out): break
    out[pos:pos + len(y)] += y; used.append({'file': s['f'], 'from_s': round(s['a'] / SR, 2), 'len_s': round(s['d'], 2), 'at_s': round(pos / SR, 2)})
    pos += len(y) + int(max(.4, gap * rng.uniform(.6, 1.4)) * SR)
X = int(XF * SR); loop = out[:L].copy(); loop[:X] += out[L:L + X]
p = np.max(np.abs(loop)); lim = 10**(-3/20)
if p > lim: loop *= lim / p
r = np.sqrt(np.mean(loop**2)); print('pieces', len(used), 'speech %.1f s' % tot, 'rms %.1f dBFS' % (20*np.log10(r)), 'peak %.1f' % (20*np.log10(np.max(np.abs(loop)))))
o = 'public/field/voices.mp3'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', o], input=loop.astype(np.float32).tobytes(), check=True)
open('public/field/voices.js', 'w').write("(window.NGOMA_FIELD=window.NGOMA_FIELD||{})['voices']='%s';\n" % base64.b64encode(open(o, 'rb').read()).decode())
c = json.load(open('public/field/cuts.json')); c['voices'] = {'pieces': used, 'kb': os.path.getsize(o) // 1024}; json.dump(c, open('public/field/cuts.json', 'w'), indent=1)
