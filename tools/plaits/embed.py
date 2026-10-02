# Puts tools/plaits/plaits.wasm into public/index.html as base64, inside <script id="plaits-wasm">. Run from the repo root after build.sh.
import base64, os, re
H = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(H, '..', '..', 'public', 'index.html')
s = open(p).read(); b = base64.b64encode(open(os.path.join(H, 'plaits.wasm'), 'rb').read()).decode()
tag = '<script id="plaits-wasm">/* Plaits by Emilie Gillet (Mutable Instruments), MIT licence, see tools/plaits */var PLAITS_WASM="' + b + '";</script>'
m = re.search(r'<script id="plaits-wasm">.*?</script>', s, re.S)
s = s[:m.start()] + tag + s[m.end():] if m else s.replace('</body>', tag + '\n</body>', 1)
open(p, 'w').write(s); print('plaits.wasm embedded,', len(b), 'chars')
