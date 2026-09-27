"""
Tests for S1Gate Remote MCP SSE Server & API Key Authentication Middleware.
Includes verification for Cloudflare Tunnels, reverse proxies, CORS, and session persistence.
"""

from __future__ import annotations

import socket
import threading
import time

import httpx
import pytest
import uvicorn
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from kevgate.sse_server import create_app


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def sse_test_server():
    """Start an ephemeral S1Gate SSE server for testing."""
    port = find_free_port()
    api_key = "secret-judge-key-12345"
    app = create_app(api_key=api_key)
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="error",
    )
    srv = uvicorn.Server(config)

    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()

    # Wait for server to bind
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            with httpx.Client() as client:
                r = client.get(f"{base_url}/health")
                if r.status_code == 200:
                    break
        except Exception:
            time.sleep(0.05)

    yield base_url, api_key

    srv.should_exit = True
    thread.join(timeout=2.0)


def test_public_health_endpoint(sse_test_server):
    """Health check endpoint should be public without authentication."""
    base_url, api_key = sse_test_server
    with httpx.Client() as client:
        response = client.get(f"{base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "S1Gate Remote MCP Server"
        assert data["auth_required"] is True
        assert "active_sessions" in data
        assert api_key not in str(data)  # Zero secrets leaked


def test_cors_options_preflight(sse_test_server):
    """CORS OPTIONS preflight request must return 204 with permissive headers."""
    base_url, _ = sse_test_server
    with httpx.Client() as client:
        response = client.options(f"{base_url}/sse")
        assert response.status_code == 204
        assert response.headers.get("access-control-allow-origin") == "*"
        assert "POST" in response.headers.get("access-control-allow-methods", "")
        assert "Authorization" in response.headers.get("access-control-allow-headers", "")


def test_unauthorized_access_rejected(sse_test_server):
    """Accessing protected MCP endpoints without valid key must return 401."""
    base_url, _ = sse_test_server
    with httpx.Client() as client:
        # Missing auth
        response = client.get(f"{base_url}/sse")
        assert response.status_code == 401
        assert "Missing or invalid S1Gate API key" in response.json()["message"]

        # Invalid Bearer
        response = client.get(f"{base_url}/sse", headers={"Authorization": "Bearer wrong-key"})
        assert response.status_code == 401

        # Invalid X-API-Key
        response = client.get(f"{base_url}/sse", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401

        # Invalid query param
        response = client.get(f"{base_url}/sse?api_key=wrong-key")
        assert response.status_code == 401


def test_authorized_access_via_bearer(sse_test_server):
    """Authorized access via Bearer token should connect to SSE endpoint with Cloudflare headers."""
    base_url, api_key = sse_test_server
    with httpx.Client() as client:
        with client.stream("GET", f"{base_url}/sse", headers={"Authorization": f"Bearer {api_key}"}) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            # Verify Cloudflare no-buffer headers
            assert response.headers.get("x-accel-buffering") == "no"
            assert "no-cache" in response.headers.get("cache-control", "")
            assert response.headers.get("access-control-allow-origin") == "*"
            first_line = next(response.iter_lines())
            assert "event: endpoint" in first_line


def test_authorized_access_via_x_api_key(sse_test_server):
    """Authorized access via X-API-Key header should connect to SSE endpoint."""
    base_url, api_key = sse_test_server
    with httpx.Client() as client:
        with client.stream("GET", f"{base_url}/sse", headers={"X-API-Key": api_key}) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            first_line = next(response.iter_lines())
            assert "event: endpoint" in first_line


def test_authorized_access_via_query_param(sse_test_server):
    """Authorized access via ?api_key= query parameter should connect to SSE endpoint."""
    base_url, api_key = sse_test_server
    with httpx.Client() as client:
        with client.stream("GET", f"{base_url}/sse?api_key={api_key}") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            first_line = next(response.iter_lines())
            assert "event: endpoint" in first_line


@pytest.mark.asyncio
async def test_full_mcp_client_with_query_param_only(sse_test_server):
    """MCP SDK Client connecting with query param only should discover all tools seamlessly."""
    base_url, api_key = sse_test_server
    async with sse_client(f"{base_url}/sse?api_key={api_key}") as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "s1gate_triage_diff" in tool_names
            assert "s1gate_inspect_file" in tool_names
            assert "s1gate_verify_remediation" in tool_names


def test_cloudflare_reverse_proxy_headers(sse_test_server):
    """Verify that Cloudflare reverse proxy headers (Host, X-Forwarded-Proto, CF-Connecting-IP) work cleanly."""
    base_url, api_key = sse_test_server
    cf_headers = {
        "Host": "mcp.subdomain.workers.dev",
        "X-Forwarded-Proto": "https",
        "CF-Connecting-IP": "198.51.100.24",
    }
    with httpx.Client() as client:
        # 1. Healthcheck with CF headers
        resp = client.get(f"{base_url}/health", headers=cf_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
        assert api_key not in resp.text

        # 2. CORS preflight with CF headers
        opt_headers = {
            **cf_headers,
            "Origin": "https://mcp.subdomain.workers.dev",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type, X-API-Key",
        }
        opt_resp = client.options(f"{base_url}/sse", headers=opt_headers)
        assert opt_resp.status_code == 204
        assert opt_resp.headers.get("access-control-allow-origin") == "*"
        assert "POST" in opt_resp.headers.get("access-control-allow-methods", "")

        # 3. Case-insensitive bearer auth
        with client.stream("GET", f"{base_url}/sse", headers={**cf_headers, "Authorization": f"bearer {api_key}"}) as bearer_resp:
            assert bearer_resp.status_code == 200
            assert "text/event-stream" in bearer_resp.headers.get("content-type", "")
            first_line = next(bearer_resp.iter_lines())
            assert "event: endpoint" in first_line


@pytest.mark.asyncio
async def test_full_mcp_client_with_cloudflare_reverse_proxy_headers(sse_test_server):
    """Full MCP Client initialization with simulated Cloudflare headers and query param auth."""
    base_url, api_key = sse_test_server
    cf_headers = {
        "Host": "mcp.subdomain.workers.dev",
        "X-Forwarded-Proto": "https",
        "CF-Connecting-IP": "198.51.100.24",
    }
    async with sse_client(f"{base_url}/sse?api_key={api_key}", headers=cf_headers) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            assert "s1gate_triage_diff" in tool_names
            assert "s1gate_inspect_file" in tool_names
            assert "s1gate_verify_remediation" in tool_names

