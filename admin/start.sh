#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/.venv"
# Database path - defaults to the canonical oc_frenchquran.sqlite
DB="${1:-$DIR/../oc_frenchquran.sqlite}"
PORT="${PORT:-5001}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
    echo "Installing dependencies..."
    "$VENV/bin/pip" install -q -r "$DIR/requirements.txt"
fi

cd "$DIR"
echo "Starting Quran Admin..."
echo "Database: $DB"
echo "Go to http://localhost:$PORT"
ADMIN_PASSWORD="$ADMIN_PASSWORD" DATABASE_PATH="$DB" PORT="$PORT" "$VENV/bin/python" run.py
