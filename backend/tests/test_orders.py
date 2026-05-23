"""Tests for /api/v1/orders endpoints."""

import pytest
from tests.conftest import make_token


class TestCreateOrder:
    async def test_create_order_success(self, async_client, parent_user, teacher_user, test_session):
        """Parent can create an order for an approved teacher."""
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()

        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher.teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["order_id"] > 0
        assert data["order_no"].startswith("HD")
        assert data["total_amount"] > 0
        # 2 hours * 100 yuan (subject unit_price) = 200
        assert data["total_amount"] == 200.0

    async def test_create_order_teacher_not_found(self, async_client, parent_user):
        """Creating order for non-existent teacher fails."""
        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": 99999,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1004  # NotFoundError

    async def test_create_order_wrong_role(self, async_client, teacher_user):
        """Teacher cannot create orders (only parent can)."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": 1,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1003  # ForbiddenError

    async def test_create_order_unauthorized(self, async_client):
        """Creating order without auth fails."""
        resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": 1,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1002  # UnauthorizedError


class TestOrderList:
    async def test_list_as_parent(self, async_client, parent_user, teacher_user, test_session):
        """Parent can list their orders."""
        # First create an order
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()

        token = make_token(parent_user.user_id, "parent")
        await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher.teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Now list
        resp = await async_client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        item = data["items"][0]
        assert item["subject"] == "数学"
        assert item["status"] == "pending_confirm"

    async def test_list_as_teacher(self, async_client, parent_user, teacher_user, test_session):
        """Teacher can list orders assigned to them."""
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()

        # Create order as parent
        parent_token = make_token(parent_user.user_id, "parent")
        await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher.teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {parent_token}"},
        )

        # List as teacher
        teacher_token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] >= 1

    async def test_list_filter_by_status(self, async_client, parent_user, teacher_user, test_session):
        """Filter orders by status."""
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()

        token = make_token(parent_user.user_id, "parent")
        await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher.teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = await async_client.get(
            "/api/v1/orders",
            params={"status": "pending_confirm"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] >= 1

        resp = await async_client.get(
            "/api/v1/orders",
            params={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] == 0


class TestOrderDetail:
    async def test_detail_as_parent(self, async_client, parent_user, teacher_user, test_session):
        """Parent can view their order detail."""
        from sqlalchemy import select
        from app.models.teacher import Teacher
        from app.models.order import Order

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()

        token = make_token(parent_user.user_id, "parent")
        create_resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher.teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        order_id = create_resp.json()["data"]["order_id"]

        resp = await async_client.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["order_id"] == order_id
        assert data["status"] == "pending_confirm"
        assert data["subject"] == "数学"


class TestFullOrderFlow:
    """Test the complete order lifecycle: pending_confirm → pending_trial → in_progress → pending_settlement → completed."""

    async def test_full_flow(self, async_client, parent_user, teacher_user, test_session):
        from sqlalchemy import select
        from app.models.teacher import Teacher
        from app.models.order import Order

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()
        teacher_id = teacher.teacher_id

        parent_token = make_token(parent_user.user_id, "parent")
        teacher_token = make_token(teacher_user.user_id, "teacher")

        # Step 1: Parent creates order
        create_resp = await async_client.post(
            "/api/v1/orders",
            json={
                "teacher_id": teacher_id,
                "subject": "数学",
                "grade": "高中",
                "lesson_date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "11:00",
            },
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert create_resp.json()["code"] == 0
        order_id = create_resp.json()["data"]["order_id"]

        # Verify status: pending_confirm
        detail = await async_client.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert detail.json()["data"]["status"] == "pending_confirm"

        # Step 2: Teacher accepts → pending_trial
        accept_resp = await async_client.post(
            f"/api/v1/orders/{order_id}/accept",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert accept_resp.json()["code"] == 0
        assert accept_resp.json()["data"]["status"] == "pending_trial"

        # Step 3: Teacher starts → in_progress
        start_resp = await async_client.post(
            f"/api/v1/orders/{order_id}/start",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert start_resp.json()["code"] == 0
        assert start_resp.json()["data"]["status"] == "in_progress"

        # Step 4: Teacher completes → pending_settlement
        complete_resp = await async_client.post(
            f"/api/v1/orders/{order_id}/complete",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert complete_resp.json()["code"] == 0
        assert complete_resp.json()["data"]["status"] == "pending_settlement"

        # Step 5: Parent confirms → completed
        confirm_resp = await async_client.post(
            f"/api/v1/orders/{order_id}/confirm",
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert confirm_resp.json()["code"] == 0
        assert confirm_resp.json()["data"]["status"] == "completed"

        # Verify final detail
        detail = await async_client.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {parent_token}"},
        )
        assert detail.json()["data"]["status"] == "completed"
