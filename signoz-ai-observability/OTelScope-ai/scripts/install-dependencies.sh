#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing direct project dependencies..."
python -m pip install -r requirements.txt

echo "Installing compatible OpenTelemetry instrumentations..."
opentelemetry-bootstrap -a install

echo "Checking dependency consistency..."
python -m pip check

echo
echo "Dependencies installed successfully."
echo "Activate the environment with:"
echo "  source .venv/bin/activate"
