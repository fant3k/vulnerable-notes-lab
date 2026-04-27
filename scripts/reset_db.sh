#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 - <<'PY'
from vuln_notes.database import init_database

init_database(reset=True)
print("Database reset completed.")
PY
