/* Quick check before deploy (v137): every inline script in Ngoma and Worp must at least compile. No browser needed.
   The full test is tools/smoke.js. */
const fs = require('fs'), path = require('path'), vm = require('vm');
let bad = 0;
for (const f of ['public/index.html', 'public/worp/index.html']) {
  const html = fs.readFileSync(path.join(__dirname, '..', f), 'utf8'), re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g; let m, i = 0;
  while ((m = re.exec(html))) { i++; const line = html.slice(0, m.index).split('\n').length;
    try { new vm.Script(m[1], { filename: f + ' (script ' + i + ', from line ' + line + ')' }); }
    catch (e) { bad++; console.log('   ' + f + ' script ' + i + ' (starts at line ' + line + '): ' + e.message); } }
}
if (bad) { console.log('   Code check failed: not deploying.'); process.exit(1); }
console.log('   Code check: all scripts compile.');
