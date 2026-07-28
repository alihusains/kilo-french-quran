#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"
DB="${1:-$DIR/../database.sqlite}"
PORT="${PORT:-5001}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q "Flask>=2.3,<3.0"
fi

cd "$DIR"
ADMIN_PASSWORD="$ADMIN_PASSWORD" DATABASE_PATH="$DB" PORT="$PORT" "$VENV/bin/python" run.py
