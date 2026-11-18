"""Security tests."""

import pytest


@pytest.mark.asyncio
async def test_password_not_in_response(client):
    """Password must never appear in any API response."""
    await client.post("/api/v1/auth/register", json={"email": "nope@test.com", "password": "SecurePass1!"})
    login = await client.post("/api/v1/auth/login", json={"email": "nope@test.com", "password": "SecurePass1!"})
    token = login.json()["access_token"]
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    data = me.json()
    assert "password" not in data
    assert "hashed_password" not in str(data)


@pytest.mark.asyncio
async def test_unauthenticated_access(client):
    """Protected endpoints must reject unauthenticated requests."""
    resp = await client.get("/api/v1/companies/")
    assert resp.status_code in (401, 403, 405)


@pytest.mark.asyncio
async def test_security_headers(client):
    """Security headers middleware must add required headers."""
    resp = await client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert "Strict-Transport-Security" in resp.headers


@pytest.mark.asyncio
async def test_weak_password_rejected(client):
    """Password must meet strength requirements."""
    resp = await client.post("/api/v1/auth/register", json={"email": "weak@test.com", "password": "short"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client):
    await client.post("/api/v1/auth/register", json={"email": "dup@test.com", "password": "SecurePass1!"})
    resp = await client.post("/api/v1/auth/register", json={"email": "dup@test.com", "password": "SecurePass1!"})
    assert resp.status_code == 409
