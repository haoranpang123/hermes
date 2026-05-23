"""Tests for /api/v1/teachers and /api/v1/teacher endpoints."""

import pytest
from tests.conftest import make_token


class TestPublicTeacherList:
    async def test_empty_list(self, async_client):
        """Public list returns empty when no approved teachers."""
        resp = await async_client.get("/api/v1/teachers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_with_approved_teacher(self, async_client, teacher_user):
        """Approved teacher appears in public list."""
        resp = await async_client.get("/api/v1/teachers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

        item = data["items"][0]
        assert item["teacher_id"] is not None
        assert item["university"] == "河南大学"
        assert item["min_price"] == 80

    async def test_list_with_filters(self, async_client, teacher_user):
        """Filter teachers by subject and gender."""
        resp = await async_client.get(
            "/api/v1/teachers",
            params={"subjects": "数学", "gender": "male"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] >= 1

    async def test_list_wrong_gender_no_results(self, async_client, teacher_user):
        """Filter female when only male exists returns empty."""
        resp = await async_client.get(
            "/api/v1/teachers",
            params={"gender": "female"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] == 0

    async def test_pending_teacher_not_listed(self, async_client, pending_teacher_user):
        """Pending teacher should NOT appear in public list."""
        resp = await async_client.get("/api/v1/teachers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["total"] == 0


class TestTeacherDetail:
    async def test_detail_approved_teacher(self, async_client, teacher_user, parent_user, test_session):
        """Get detail of an approved teacher (requires auth)."""
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == teacher_user.user_id)
        )
        teacher = result.scalar_one()
        teacher_id = teacher.teacher_id

        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.get(
            f"/api/v1/teachers/{teacher_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["teacher_id"] == teacher_id
        assert data["real_name"] == "张老师"
        assert data["university"] == "河南大学"
        assert data["is_available"] is True

    async def test_detail_not_found(self, async_client, parent_user):
        """Non-existent teacher returns error (requires auth)."""
        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.get(
            "/api/v1/teachers/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1004  # NotFoundError

    async def test_detail_pending_not_found(self, async_client, pending_teacher_user, parent_user, test_session):
        """Pending teacher should not be accessible via detail endpoint."""
        from sqlalchemy import select
        from app.models.teacher import Teacher

        result = await test_session.execute(
            select(Teacher).where(Teacher.user_id == pending_teacher_user.user_id)
        )
        teacher = result.scalar_one()
        teacher_id = teacher.teacher_id

        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.get(
            f"/api/v1/teachers/{teacher_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1004  # Not found (only approved teachers visible)


class TestTeacherApply:
    async def test_apply_success(self, async_client, fresh_user):
        """Teacher can submit an application."""
        # First select teacher role
        token = make_token(fresh_user.user_id, None)
        await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "teacher"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get fresh token WITH role
        token = make_token(fresh_user.user_id, "teacher")

        resp = await async_client.post(
            "/api/v1/teacher/apply",
            json={
                "real_name": "王老师",
                "gender": "male",
                "university": "河南大学",
                "major": "物理",
                "grade": "研一",
                "bio": "热爱教学",
                "min_price": 90,
                "teaching_regions": ["金明区"],
                "subjects": [
                    {"subject": "物理", "grade_level": "高中", "unit_price": 100}
                ],
                "schedules": [
                    {"day_of_week": 2, "start_time": "09:00", "end_time": "11:00"}
                ],
                "certificates": [
                    {"cert_type": "student_card", "image_url": "http://example.com/cert.jpg"}
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["teacher_id"] > 0
        assert data["audit_status"] == "pending"

    async def test_apply_duplicate_fails(self, async_client, teacher_user):
        """Cannot apply twice."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.post(
            "/api/v1/teacher/apply",
            json={
                "real_name": "再申请",
                "gender": "male",
                "university": "河南大学",
                "major": "化学",
                "grade": "大三",
                "subjects": [{"subject": "化学", "grade_level": "初中", "unit_price": 80}],
                "schedules": [{"day_of_week": 1, "start_time": "08:00", "end_time": "10:00"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1005  # BusinessError: already applied

    async def test_apply_wrong_role(self, async_client, parent_user):
        """Parent cannot submit teacher application."""
        token = make_token(parent_user.user_id, "parent")
        resp = await async_client.post(
            "/api/v1/teacher/apply",
            json={
                "real_name": "家长假装老师",
                "gender": "male",
                "university": "河南大学",
                "major": "数学",
                "grade": "大三",
                "subjects": [{"subject": "数学", "grade_level": "初中", "unit_price": 70}],
                "schedules": [{"day_of_week": 1, "start_time": "08:00", "end_time": "10:00"}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1003  # ForbiddenError


class TestTeacherStatus:
    async def test_get_status(self, async_client, teacher_user):
        """Teacher can view their audit status."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.get(
            "/api/v1/teacher/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["audit_status"] == "approved"

    async def test_get_status_no_teacher_record(self, async_client, fresh_user):
        """User with teacher role but no Teacher record gets error."""
        token = make_token(fresh_user.user_id, None)
        await async_client.post(
            "/api/v1/auth/select-role",
            json={"role": "teacher"},
            headers={"Authorization": f"Bearer {token}"},
        )
        token = make_token(fresh_user.user_id, "teacher")
        resp = await async_client.get(
            "/api/v1/teacher/status",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 1004  # NotFoundError: no Teacher record


class TestTeacherProfile:
    async def test_get_profile(self, async_client, teacher_user):
        """Teacher can get full profile."""
        token = make_token(teacher_user.user_id, "teacher")
        resp = await async_client.get(
            "/api/v1/teacher/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["real_name"] == "张老师"
        assert data["university"] == "河南大学"
        assert len(data["subjects"]) >= 1
        assert data["subjects"][0]["subject"] == "数学"
        assert len(data["schedules"]) >= 1
