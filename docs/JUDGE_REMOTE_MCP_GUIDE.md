# Judge & Evaluator Guide: S1Gate Hosted Remote MCP Server

This guide provides instructions for hackathon judges and evaluators to connect to the **S1Gate Remote Model Context Protocol (MCP) Server** via Server-Sent Events (SSE).

---

## 1. Remote Server Architecture

Instead of requiring local installation or Python environment setup, S1Gate provides a hosted, remote MCP endpoint compatible with the **Model Context Protocol (v2.0)** standard.

```
┌──────────────────────────────────────┐
│     Client (Judge Environment)       │
│  • IBM Bob IDE (mcp.json)            │
│  • Claude Code / Claude Desktop      │
│  • Agrav / Kiro / Custom MCP Client  │
└──────────────────┬───────────────────┘
                   │  HTTP SSE + JSON-RPC
                   │  (Bearer / X-API-Key / ?api_key=)
                   ▼
┌──────────────────────────────────────┐
│       S1Gate Remote MCP Server       │
│  • Port 8000 / /sse & /messages/     │
│  • API Key Authentication Middleware │
│  • Pure ASGI Streaming Transport     │
└──────────────────┬───────────────────┘
                   │  System-1 Inference Loop
                   ▼
┌──────────────────────────────────────┐
│       Google Gemini 3.5 Flash        │
│  • Sub-1.5s Structured Triage        │
│  • Pre-Commit Invariant Validation   │
└──────────────────────────────────────┘
```

---

## 2. Server Authentication

To prevent unauthorized public compute abuse, the remote MCP endpoint is locked behind an API key.

Judges can authenticate using **any** of the following three methods:

| Method | Syntax | Best For |
| :--- | :--- | :--- |
| **HTTP Authorization Header** | `Authorization: Bearer <API_KEY>` | Standard MCP Clients (Bob IDE, Claude) |
| **Custom Header** | `X-API-Key: <API_KEY>` | API Gateways & Reverse Proxies |
| **Query Parameter** | `https://<HOST>/sse?api_key=<API_KEY>` | Web browsers, EventSource, curl |

---

## 3. Quick Connection Guide for Judges

### Option A: Connect via IBM Bob IDE

In your workspace, edit or create `.bob/mcp.json` (or global MCP settings):

```json
{
  "mcpServers": {
    "s1gate": {
      "url": "http://10.20.20.11:8000/sse",
      "headers": {
        "Authorization": "Bearer <JUDGE_API_KEY>"
      }
    }
  }
}
```

*Alternatively, using the URL query parameter:*
```json
{
  "mcpServers": {
    "s1gate": {
      "url": "http://10.20.20.11:8000/sse?api_key=<JUDGE_API_KEY>"
    }
  }
}
```

Once saved, Bob IDE will discover all three S1Gate tools:
1. `s1gate_triage_diff`: Full unified git diff risk evaluation.
2. `s1gate_inspect_file`: Staged file change inspection.
3. `s1gate_verify_remediation`: Actor-critic patch verification.

---

### Option B: Connect via Claude Code / Claude Desktop

In `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "s1gate": {
      "url": "http://10.20.20.11:8000/sse",
      "headers": {
        "Authorization": "Bearer <JUDGE_API_KEY>"
      }
    }
  }
}
```

---

### Option C: Instant Health & Connection Verification (cURL)

Verify the remote server in 5 seconds from your terminal:

#### 1. Public Health Check (No Auth Required)
```bash
curl -s http://10.20.20.11:8000/health | jq
```
*Expected Output:*
```json
{
  "status": "healthy",
  "service": "S1Gate Remote MCP Server",
  "version": "0.1.0",
  "backend": "gemini",
  "model": "gemini-3.5-flash-lite",
  "auth_required": true
}
```

#### 2. Test Protected Endpoint with API Key
```bash
curl -N -H "Authorization: Bearer <JUDGE_API_KEY>" http://10.20.20.11:8000/sse
```
*Expected Output:*
```text
event: endpoint
data: /messages/?session_id=...
```

---

## 4. Hosting & Running Your Own S1Gate Instance

If judges prefer to host their own instance:

### 1-Command Startup with Docker Compose
```bash
git clone https://github.com/WilliamAxelC/IBM-hackathon.git
cd IBM-hackathon
export GEMINI_API_KEY="your-gemini-key"
export S1GATE_SERVER_API_KEY="judge-secret-key"
docker compose -f docker-compose.sse.yml up -d
```

### Local Python Native Run
```bash
uv pip install -e .
python -m kevgate.sse_server --host 0.0.0.0 --port 8000 --api-key "judge-secret-key"
```

---

## 5. Security & Isolation Guarantees

- **Zero Secret Leakage**: The `/health` endpoint exposes zero keys or credentials.
- **Pure ASGI Streaming**: SSE connections are streamed natively without response buffering, preventing denial-of-service hangs.
- **DNS Rebinding & Reverse Proxy Safe**: Built-in transport security configuration supports TLS reverse proxies (Traefik, Caddy, NGINX, Cloudflare) without HTTP 421 host header rejections.
