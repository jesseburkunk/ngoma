#!/bin/sh
# Deploy Ngoma (and Worp at /worp) to Cloudflare Pages. Run from anywhere: ./deploy.sh  (or: sh deploy.sh)
set -e
cd "$(dirname "$0")"
W="npx --yes wrangler@latest"

command -v node >/dev/null 2>&1 || { echo "Node.js not found. Install it first: brew install node"; exit 1; }
echo "1/4 Worp engine: copying the latest Worp sound engine into Ngoma's Worp pad..."
if python3 -c "" >/dev/null 2>&1; then python3 tools/sync_worp.py || echo "   Sync failed; deploying with the engine Ngoma already has."; else echo "   python3 not available; skipped (the Worp pad keeps its current engine)."; fi

echo "   Checking the code..."
node tools/check.js || exit 1
if node -e "require('playwright')" >/dev/null 2>&1; then echo "   Playwright found: running the full test (about two minutes)..."; node tools/smoke.js || { echo "   Test failed: not deploying. Deploy anyway with: SKIP_TEST=1 sh deploy.sh"; [ -n "$SKIP_TEST" ] || exit 1; }; fi

echo "2/4 Checking your Cloudflare login (the first time npx downloads wrangler, that can take a minute)..."
$W whoami >/dev/null 2>&1 || $W login

echo "3/4 Checking the Pages project..."
$W pages project list 2>/dev/null | grep -qw "ngoma" || $W pages project create ngoma --production-branch main || true

echo "4/4 Uploading public/ (Ngoma and Worp)..."
$W pages deploy public --project-name ngoma --branch main --commit-dirty=true
echo "Done. Ngoma: https://ngoma.pages.dev  Worp: https://ngoma.pages.dev/worp/  (refresh with Cmd+Shift+R)"
