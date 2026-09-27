#!/usr/bin/env bash
# ==============================================================================
# S1Gate Remote MCP Server + Cloudflare Tunnel Launcher
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BIN_DIR="${PROJECT_ROOT}/bin"
PORT="${S1GATE_PORT:-8000}"
API_KEY="${S1GATE_SERVER_API_KEY:-s1gate-judge-key-2026}"

echo "================================================================="
echo "   S1Gate Remote MCP Server & Cloudflare Reverse Proxy Launcher   "
echo "================================================================="

# 1. Check Python virtual environment
if [ -d "${PROJECT_ROOT}/.venv" ]; then
    PYTHON="${PROJECT_ROOT}/.venv/bin/python"
else
    PYTHON="python3"
fi

# 2. Check cloudflared binary
CLOUDFLARED_BIN=""
if command -v cloudflared &> /dev/null; then
    CLOUDFLARED_BIN="cloudflared"
elif [ -f "${BIN_DIR}/cloudflared" ]; then
    CLOUDFLARED_BIN="${BIN_DIR}/cloudflared"
else
    echo "[*] cloudflared not found in PATH."
    echo "[*] Downloading official cloudflared binary to ./bin/cloudflared..."
    mkdir -p "${BIN_DIR}"
    curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64" -o "${BIN_DIR}/cloudflared"
    chmod +x "${BIN_DIR}/cloudflared"
    CLOUDFLARED_BIN="${BIN_DIR}/cloudflared"
    echo "[+] cloudflared installed to ${CLOUDFLARED_BIN}"
fi

# 3. Start S1Gate SSE Server in background
echo "[*] Starting S1Gate Remote MCP Server on 127.0.0.1:${PORT}..."
echo "[*] Server API Key: ${API_KEY}"

"${PYTHON}" -m kevgate.sse_server --host 127.0.0.1 --port "${PORT}" --api-key "${API_KEY}" &
SERVER_PID=$!

cleanup() {
    echo ""
    echo "[*] Shutting down S1Gate server (PID: ${SERVER_PID})..."
    kill "${SERVER_PID}" 2>/dev/null || true
    wait "${SERVER_PID}" 2>/dev/null || true
    echo "[+] Done."
}
trap cleanup EXIT INT TERM

# Wait for server to be healthy
echo "[*] Waiting for server healthcheck..."
for i in {1..30}; do
    if curl -s "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
        echo "[+] S1Gate local server is healthy!"
        break
    fi
    sleep 0.5
done

# 4. Start Cloudflare Tunnel
echo "================================================================="
echo "[*] Launching Cloudflare Tunnel pointing to http://127.0.0.1:${PORT}..."
echo "[*] Look for the 'https://*.trycloudflare.com' URL below:"
echo "================================================================="

"${CLOUDFLARED_BIN}" tunnel --url "http://127.0.0.1:${PORT}"
