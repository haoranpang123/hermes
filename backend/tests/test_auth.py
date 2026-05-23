"""Tests for /api/v1/auth endpoints."""

import pytest
from tests.conftest import make_token


class TestLogin:
    async def test_login_mock(self, async_client):
        """Login with mock mode returns token + user_info."""
        resp = await async_client.post("/api/v1/auth/login", json={"code": "test_code"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["message"] == "ok"
        data = body["data"]
        assert "token" in data
        assert len(data["token"]) > 10
        assert data["user_info"]["nickname"] == "微信用户"
        assert data["is_new"] is True

    async def test_login_empty_code(self, async_client):
        """Empty code should return validation error."""
        resp = await async_client.post("/api/v1/auth/login", json={"code": ""})
        # FastAPI returns 422 for validation errors
        assert resp.status_code == 422

    async def test_login_creates_wallet(self, async_client, test_session):
        """Login should auto-create a wallet for new users."""
        resp = await async_client.post("/api/v1/auth/login", json={"code": "new_user"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0

        # Verify wallet was created
        from app.models.wallet import Wallet
        from sqlalchemy import select

        user_id = body["data"]["user_info"]["user_id"]
        result = await test_session.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = result.scalar_one_or_none()
        assert wallet is not None
        assert wallet.balance == 0


class TestProfile:
    async def test_get_profile_unauthorized(self, async_client):
        """Profile endpoint requires auth."""
        resp = await async_client.get("/api/v1/auth/profile")
        assert resp.status_code == 200  # AppException returns 200 with error code
        body = resp.json()
        assert body["code"] == 1002  # UnauthorizedError

    async def test_get_profile(self, async_client, parent_user):
        """Authenticated user can get their profile."""
        token = make_token(parent_user.user_id, parent_user.role)
        resp = await async_client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["user_id"] == parent_user.user_id
        assert data["nickname"] == "家长测试"
        assert data["role"] == "parent"
        assert data["has_selected_role"] is True

    async def test_update_profile(self, async_client, parent_user):
        """Authenticated user can update nickname and avatar."""
        token = make_token(parent_user.user_id, parent_user.role)
        resp = await async_client.put(
            "/api/v1/auth/profile",
            json={"nickname": "新昵称", "avatar_url": "https://example.com/avatar.png"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["nickname"] == "新昵称"
        assert body["data"]["avatar_url"] == "https://example.com/avatar.png"

    async def test_update_profile_partial(self, async_client, parent_user):
        """Update only nickname, leaving avatar unchanged."""
        token = make_token(parent_user.user_id, parent_user.role)
        resp = await async_client.put(
            "/api/v1/auth/profile",
            json={"nickname": "仅更新昵称"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["nickname"] == "仅更新昵称"


class TestBindPhone:
    async def test_bind_phone(self, async_client, test_session):
        """Bind phone number for a user without phone."""
        # Create a user without phone
        from app.models.user import User
        from app.models.wallet import Wallet
        u = User(openid="test_nophone", nickname="无手机号", role="parent", status=1)
        test_session.add(u)
        await test_session.flush()
        w = Wallet(user_id=u.user_id, balance=0)
        test_session.add(w)
        await test_session.flush()
        await test_session.commit()

        token = make_token(u.user_id, "parent")
        resp = await async_client.post(
            "/api/v1/auth/bind-phone",
            json={"code": "mock_phone_code"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "phone" in body["data"]
        # Phone should be masked
        assert "****" in body["data"]["phone"]

    async def test_bind_phone_already_bound(self, async_client, parent_user):
        """Cannot bind phone twice."""
        token = make_token(parent_user.user_id, parent_user.role)

        # First bind
        await async_client.post(
            "/api/v1/auth/bind-phone",
            json={"code": "mock_phone_code"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Second bind — should fail
        resp = await async_client.post(
            "/api/v1/auth/bind-phone",
            json={"code": "mock_phone_code_2"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1005  # BusinessError


class TestSelectRole:
    async def test_select_role_parent(self, async_client, fresh_user):
        """Fresh user selects parent role."""
        token = make_token(fresh_user.user_id, None)
        resp = await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "parent"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["role"] == "parent"
        assert data["user_id"] == fresh_user.user_id
        assert data["need_teacher_apply"] is False

    async def test_select_role_teacher(self, async_client, fresh_user):
        """Fresh user selects teacher role."""
        token = make_token(fresh_user.user_id, None)
        resp = await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "teacher"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["role"] == "teacher"
        assert data["need_teacher_apply"] is True

    async def test_select_role_twice_fails(self, async_client, parent_user):
        """User who already selected a role cannot change it."""
        token = make_token(parent_user.user_id, parent_user.role)
        resp = await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "teacher"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1005  # BusinessError

    async def test_select_invalid_role(self, async_client, fresh_user):
        """Select role fails for invalid role."""
        token = make_token(fresh_user.user_id, None)
        resp = await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422  # Pydantic validation

