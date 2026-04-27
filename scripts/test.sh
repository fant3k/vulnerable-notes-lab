#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -B -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/tmp/vulnerable_notes_pycache python3 -m compileall vuln_notes
