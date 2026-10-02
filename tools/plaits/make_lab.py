# Builds public/lab-plaits.html: lab_template.html + the Worp engine from public/index.html + plaits.wasm as base64.
# Run from the repo root: python3 tools/plaits/make_lab.py
import base64, re, os
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..', '..')
s = open(os.path.join(R, 'public', 'index.html')).read()
a = s.index('/* Worp engine for Ngoma'); z = re.compile(r'window\.WorpEngine=\{[^\n]*\};\n\}\)\(\);\n').search(s, a).end()
t = open(os.path.join(H, 'lab_template.html')).read()
t = t.replace('/*ENGINE*/', s[a:z]).replace('%%WASM%%', base64.b64encode(open(os.path.join(H, 'plaits.wasm'), 'rb').read()).decode())
open(os.path.join(R, 'public', 'lab-plaits.html'), 'w').write(t); print('public/lab-plaits.html', len(t), 'bytes')
