#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
node -e 'if(process.versions.node !== "24.19.0") throw new Error("Wymagany Node.js 24.19.0 (patrz .nvmrc)")'
npm ci --no-fund --no-audit
if command -v chromium >/dev/null 2>&1; then
  chromium --version
else
  npx playwright install chromium
fi
