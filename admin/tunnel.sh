#!/bin/bash
set -e

# Quick tunnel for sharing the admin panel with non-technical users.
# Uses cloudflared (Cloudflare Tunnel) if available, otherwise falls back to localtunnel.

PORT="${PORT:-5001}"

if command -v cloudflared >/dev/null 2>&1; then
    echo "Starting Cloudflare Tunnel on port $PORT..."
    cloudflared tunnel --url "http://localhost:$PORT"
elif command -v lt >/dev/null 2>&1; then
    echo "Starting localtunnel on port $PORT..."
    lt --port "$PORT"
elif [ -f "$HOME/.cloudflared/bin/cloudflared" ]; then
    echo "Starting Cloudflare Tunnel on port $PORT..."
    "$HOME/.cloudflared/bin/cloudflared" tunnel --url "http://localhost:$PORT"
else
    echo "No tunnel tool found. Install one of the following:"
    echo ""
    echo "  brew install cloudflared      # macOS (recommended)"
    echo "  npm install -g localtunnel     # Node.js alternative"
    echo ""
    echo "Then re-run: ./tunnel.sh"
    exit 1
fi
