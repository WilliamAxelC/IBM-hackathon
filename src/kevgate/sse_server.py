"""
S1Gate Remote MCP Server (SSE / HTTP Transport with API Key Authentication).

Provides a hosted, remotely accessible MCP server for hackathon judges and client agents.
Optimized for Cloudflare Tunnels, reverse proxies, and direct internet access.

Supported Authentication Methods:
  1. HTTP Header:       Authorization: Bearer <API_KEY>
  2. Custom Header:     X-API-Key: <API_KEY>
  3. Query Parameter:   https://your-domain.com/sse?api_key=<API_KEY>

Cloudflare / Reverse Proxy Features:
  - Automatic Session ID authorization tracking across SSE and POST messages.
  - Cloudflare no-buffer headers (X-Accel-Buffering: no, Cache-Control: no-cache, no-transform).
  - CORS preflight (OPTIONS) support for web clients.
  - Proxy header forwarding (X-Forwarded-Proto, CF-Connecting-IP).

Usage:
  python -m kevgate.sse_server --host 0.0.0.0 --port 8000 --api-key <YOUR_KEY>

Configuration in Bob IDE / Claude Code (mcp.json):
  {
    "mcpServers": {
      "s1gate": {
        "url": "https://s1gate.example.com/sse",
        "headers": {
          "Authorization": "Bearer <YOUR_KEY>"
        }
      }
    }
  }

Or via query parameter:
  {
    "mcpServers": {
      "s1gate": {
        "url": "https://s1gate.example.com/sse?api_key=<YOUR_KEY>"
      }
    }
  }
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Callable, Optional
from urllib.parse import parse_qs

import uvicorn
from mcp.server.sse import TransportSecuritySettings

from kevgate.config import S1GateConfig
from kevgate.mcp_server import server


class APIKeyAuthMiddleware:
    """
    Pure ASGI middleware for API Key authentication and Cloudflare reverse-proxy support.
    
    Compatible with long-lived SSE streaming connections (avoids Starlette
    BaseHTTPMiddleware response buffering assertion errors).
    """

    def __init__(self, app: Any, required_api_key: Optional[str] = None):
        self.app = app
        self.required_api_key = required_api_key or os.getenv("S1GATE_SERVER_API_KEY", "")
        self.authenticated_sessions: set[str] = set()

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET").upper()
        path = scope.get("path", "")

        # 1. Handle CORS preflight OPTIONS requests for Cloudflare & browser MCP clients
        if method == "OPTIONS":
            cors_headers = [
                (b"access-control-allow-origin", b"*"),
                (b"access-control-allow-methods", b"GET, POST, OPTIONS"),
                (b"access-control-allow-headers", b"Authorization, Content-Type, X-API-Key, Accept, Last-Event-ID, Cache-Control, X-Requested-With, Origin"),
                (b"access-control-max-age", b"86400"),
                (b"content-length", b"0"),
            ]
            await send({"type": "http.response.start", "status": 204, "headers": cors_headers})
            await send({"type": "http.response.body", "body": b""})
            return

        # 2. Public health check endpoint
        if path in ("/health", "/"):
            config = S1GateConfig()
            body = json.dumps({
                "status": "healthy",
                "service": "S1Gate Remote MCP Server",
                "version": "0.1.0",
                "backend": config.backend,
                "model": config.gemini_model if config.backend == "gemini" else config.lmstudio_model,
                "auth_required": bool(self.required_api_key),
                "active_sessions": len(self.authenticated_sessions),
            }).encode("utf-8")
            headers = [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
                (b"access-control-allow-origin", b"*"),
            ]
            await send({"type": "http.response.start", "status": 200, "headers": headers})
            await send({"type": "http.response.body", "body": body})
            return

        # 3. Authentication verification
        if self.required_api_key:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("latin1").strip()
            x_api_key = headers.get(b"x-api-key", b"").decode("latin1").strip()
            query_string = scope.get("query_string", b"").decode("latin1")
            params = parse_qs(query_string)
            query_key = params.get("api_key", [None])[0] or params.get("token", [None])[0]
            session_id = params.get("session_id", [None])[0]

            valid = False
            if auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()
                if token == self.required_api_key:
                    valid = True
            elif x_api_key == self.required_api_key:
                valid = True
            elif query_key == self.required_api_key:
                valid = True
            elif session_id and (
                session_id in self.authenticated_sessions
                or session_id.replace("-", "") in self.authenticated_sessions
            ):
                valid = True

            if not valid:
                err_body = json.dumps({
                    "error": "Unauthorized",
                    "message": "Missing or invalid S1Gate API key. Provide 'Authorization: Bearer <KEY>', 'X-API-Key: <KEY>', or '?api_key=<KEY>'.",
                }).encode("utf-8")
                resp_headers = [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(err_body)).encode("ascii")),
                    (b"access-control-allow-origin", b"*"),
                ]
                await send({"type": "http.response.start", "status": 401, "headers": resp_headers})
                await send({"type": "http.response.body", "body": err_body})
                return

        # 4. Intercept send to track session IDs and inject Cloudflare SSE headers
        async def wrapped_send(message: dict) -> None:
            if message["type"] == "http.response.start":
                # Inject Cloudflare-friendly no-buffer headers & CORS on responses
                orig_headers = list(message.get("headers", []))
                existing = {h[0].lower() for h in orig_headers}
                if b"access-control-allow-origin" not in existing:
                    orig_headers.append((b"access-control-allow-origin", b"*"))
                if b"access-control-allow-methods" not in existing:
                    orig_headers.append((b"access-control-allow-methods", b"GET, POST, OPTIONS"))
                if b"x-accel-buffering" not in existing:
                    orig_headers.append((b"x-accel-buffering", b"no"))
                # Ensure Cloudflare does not transform or buffer SSE chunks
                orig_headers = [h for h in orig_headers if h[0].lower() != b"cache-control"]
                orig_headers.append((b"cache-control", b"no-cache, no-transform, no-store"))
                message["headers"] = orig_headers
            elif message["type"] == "http.response.body":
                body_bytes = message.get("body", b"")
                if b"session_id=" in body_bytes:
                    m = re.search(r"session_id=([0-9a-fA-F\-]+)", body_bytes.decode("utf-8", errors="ignore"))
                    if m:
                        raw_sid = m.group(1)
                        self.authenticated_sessions.add(raw_sid)
                        self.authenticated_sessions.add(raw_sid.replace("-", ""))
            await send(message)

        await self.app(scope, receive, wrapped_send)


def create_app(api_key: Optional[str] = None):
    """Create the Starlette application wrapping the MCP SSE transport with auth middleware."""
    # Allow hosted reverse proxies and custom domains without DNS rebinding rejection
    security_settings = TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=["*"],
    )
    # Base MCP SSE application with /sse and /messages/ endpoints
    base_app = server.sse_app(transport_security=security_settings)
    return APIKeyAuthMiddleware(base_app, required_api_key=api_key)


def main():
    parser = argparse.ArgumentParser(description="Run S1Gate Remote MCP Server (SSE)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--api-key", default=None, help="API key to protect the server with (or set S1GATE_SERVER_API_KEY)")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("S1GATE_SERVER_API_KEY")
    if not api_key:
        print("[s1gate-sse] WARNING: No API key specified! Server is running in UNPROTECTED public mode.", file=sys.stderr)
    else:
        masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print(f"[s1gate-sse] API Key authentication active (Key: {masked})")

    app = create_app(api_key)
    print(f"[s1gate-sse] Starting S1Gate Remote MCP Server on http://{args.host}:{args.port}/sse")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="info",
    )


if __name__ == "__main__":
    main()
