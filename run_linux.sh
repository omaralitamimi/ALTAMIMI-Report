#!/usr/bin/env bash
set -e
PYTHON=""
for p in python3.14 python3.13 python3.12 python3.11; do
  if command -v "$p" >/dev/null 2>&1; then PYTHON="$p"; break; fi
done
if [ -z "$PYTHON" ]; then
  echo "Python 3.11 or newer is required."
  exit 1
fi
[ -d .venv ] || "$PYTHON" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
