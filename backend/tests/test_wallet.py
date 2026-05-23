"""Tests for /api/v1/wallet endpoints."""

import pytest
from tests.conftest import make_token


class TestGetWallet:
    async def test_get_wallet_success(self, async_client, parent_user):
        """Parent can view their wallet balance."""
        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.get(
            "/api/v1/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert "balance" in data
        assert data["balance"] == 100  # From fixture

    async def test_get_wallet_unauthorized(self, async_client):
        """Wallet endpoint requires auth."""
        resp = await async_client.get("/api/v1/wallet")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1002  # UnauthorizedError

    async def test_get_wallet_wrong_role(self, async_client, teacher_user):
        """Teacher cannot access wallet (parent only)."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.get(
            "/api/v1/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1003  # ForbiddenError


class TestRecharge:
    async def test_recharge_success(self, async_client, parent_user):
        """Parent can recharge coins."""
        token = make_token(parent_user.user_id, "parent")

        # Current balance
        get_resp = await async_client.get(
            "/api/v1/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        old_balance = get_resp.json()["data"]["balance"]

        # Recharge 50 coins
        resp = await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 50},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["amount"] == 50
        assert data["coins"] == 50

        # Verify balance increased
        get_resp = await async_client.get(
            "/api/v1/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        new_balance = get_resp.json()["data"]["balance"]
        assert new_balance == old_balance + 50

    async def test_recharge_multiple(self, async_client, parent_user):
        """Multiple recharges accumulate."""
        token = make_token(parent_user.user_id, "parent")

        await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 30},
            headers={"Authorization": f"Bearer {token}"},
        )
        await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 70},
            headers={"Authorization": f"Bearer {token}"},
        )

        get_resp = await async_client.get(
            "/api/v1/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.json()["data"]["balance"] == 200  # 100 initial + 30 + 70

    async def test_recharge_wrong_role(self, async_client, teacher_user):
        """Teacher cannot recharge."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 50},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1003  # ForbiddenError


class TestTransactions:
    async def test_transactions_empty(self, async_client, parent_user):
        """New wallet has no transactions until recharge."""
        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.get(
            "/api/v1/wallet/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] == 0
        assert data["items"] == []

    async def test_transactions_after_recharge(self, async_client, parent_user):
        """Transactions list shows recharge records."""
        token = make_token(parent_user.user_id, "parent")

        # Do a recharge
        await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 50},
            headers={"Authorization": f"Bearer {token}"},
        )

        # List transactions
        resp = await async_client.get(
            "/api/v1/wallet/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] >= 1
        txn = data["items"][0]
        assert txn["type"] == "recharge"
        assert txn["amount"] == 50

    async def test_transactions_multiple(self, async_client, parent_user):
        """Multiple transactions appear in order."""
        token = make_token(parent_user.user_id, "parent")

        await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 20},
            headers={"Authorization": f"Bearer {token}"},
        )
        await async_client.post(
            "/api/v1/wallet/recharge",
            json={"amount": 30},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = await async_client.get(
            "/api/v1/wallet/transactions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] == 2
