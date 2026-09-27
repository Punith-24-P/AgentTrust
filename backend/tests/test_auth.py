import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_auth_registration_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = f"alex.{uuid.uuid4().hex[:8]}@agenttrust.ai"
        # 1. Register new user
        reg_payload = {
            "name": "Alex Mercer",
            "email": unique_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        }
        res = await ac.post("/api/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == unique_email
        assert data["workspace_id"] is not None
        token = data["access_token"]

        # 2. Duplicate registration should fail
        res_dup = await ac.post("/api/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Access protected route /api/auth/me
        res_me = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        assert res_me.json()["email"] == unique_email

        # 4. Access protected route without token should fail
        res_unauth = await ac.get("/api/auth/me")
        assert res_unauth.status_code == 401

        # 5. Login with invalid password
        res_fail_login = await ac.post("/api/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        assert res_fail_login.status_code == 401

        # 6. Login with valid password
        res_login = await ac.post("/api/auth/login", json={
            "email": unique_email,
            "password": "Password123!",
            "remember": True
        })
        assert res_login.status_code == 200
        assert "access_token" in res_login.json()
