"""Pytest fixtures for backend API tests.

Uses SQLite in-memory (via aiosqlite) to avoid needing a real MySQL.
Overrides get_db to inject the test session.
"""

import pytest
import pytest_asyncio
from datetime import datetime, date, time
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Fix: On SQLite, BigInteger must render as INTEGER so autoincrement works.
# SQLAlchemy's BigInteger on SQLite produces BIGINT which doesn't trigger
# SQLite's rowid alias → INSERT fails with NOT NULL on PK.
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles


@compiles(BigInteger, "sqlite")
def _compile_bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"


# ---------------------------------------------------------------------------
# We must configure the app *before* importing it so that any module-level
# code that depends on the test DB is happy.  The actual FastAPI app is
# created at import time, so we monkey-patch settings first.
# ---------------------------------------------------------------------------
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.core.security import create_access_token  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a fresh SQLite engine + tables for each test function."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """Yield an AsyncSession bound to the test engine."""
    factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(test_session):
    """Return an httpx.AsyncClient that talks directly to the FastAPI app.

    Overrides get_db so that every request uses *test_session*.
    """

    async def override_get_db():
        try:
            yield test_session
            await test_session.commit()
        except Exception:
            await test_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper factories for test data
# ---------------------------------------------------------------------------

def make_token(user_id: int, role: str | None = None) -> str:
    """Create a valid JWT for the given user."""
    return create_access_token(user_id=user_id, role=role)


@pytest_asyncio.fixture
async def parent_user(test_session: AsyncSession):
    """Create a parent user and its wallet directly in the DB."""
    from app.models.user import User
    from app.models.wallet import Wallet

    u = User(
        openid="test_parent_openid",
        nickname="家长测试",
        avatar_url=None,
        phone="13800000001",
        role="parent",
        status=1,
    )
    test_session.add(u)
    await test_session.flush()

    w = Wallet(user_id=u.user_id, balance=100)
    test_session.add(w)
    await test_session.flush()
    await test_session.commit()
    return u


@pytest_asyncio.fixture
async def teacher_user(test_session: AsyncSession):
    """Create a teacher user + approved Teacher record directly in the DB."""
    from app.models.user import User
    from app.models.teacher import Teacher
    from app.models.teacher_subject import TeacherSubject
    from app.models.teacher_schedule import TeacherSchedule
    from app.models.wallet import Wallet

    u = User(
        openid="test_teacher_openid",
        nickname="教师测试",
        avatar_url=None,
        phone="13800000002",
        role="teacher",
        status=1,
    )
    test_session.add(u)
    await test_session.flush()

    t = Teacher(
        user_id=u.user_id,
        real_name="张老师",
        gender="male",
        university="河南大学",
        major="数学",
        grade="大三",
        bio="资深家教",
        min_price=80,
        teaching_regions='["龙亭区","鼓楼区"]',
        audit_status="approved",
        is_available=1,
    )
    test_session.add(t)
    await test_session.flush()

    # Add a subject so order creation works
    subj = TeacherSubject(
        teacher_id=t.teacher_id,
        subject="数学",
        grade_level="高中",
        unit_price=100,
    )
    test_session.add(subj)

    # Add a schedule
    sched = TeacherSchedule(
        teacher_id=t.teacher_id,
        day_of_week=1,
        start_time=time(8, 0),
        end_time=time(10, 0),
        status="available",
    )
    test_session.add(sched)

    w = Wallet(user_id=u.user_id, balance=0)
    test_session.add(w)
    await test_session.flush()
    await test_session.commit()
    return u


@pytest_asyncio.fixture
async def pending_teacher_user(test_session: AsyncSession):
    """Create a teacher user whose Teacher record is still pending."""
    from app.models.user import User
    from app.models.teacher import Teacher
    from app.models.wallet import Wallet

    u = User(
        openid="test_pending_teacher_openid",
        nickname="待审核教师",
        role="teacher",
        status=1,
    )
    test_session.add(u)
    await test_session.flush()

    t = Teacher(
        user_id=u.user_id,
        real_name="李老师",
        gender="female",
        university="河南大学",
        major="英语",
        grade="大二",
        audit_status="pending",
        is_available=1,
    )
    test_session.add(t)
    w = Wallet(user_id=u.user_id, balance=0)
    test_session.add(w)
    await test_session.flush()
    await test_session.commit()
    return u


@pytest_asyncio.fixture
async def fresh_user(test_session: AsyncSession):
    """Create a fresh user with no role selected yet."""
    from app.models.user import User
    from app.models.wallet import Wallet

    u = User(
        openid="test_fresh_openid",
        nickname="新用户",
        role=None,
        status=1,
    )
    test_session.add(u)
    await test_session.flush()

    w = Wallet(user_id=u.user_id, balance=0)
    test_session.add(w)
    await test_session.flush()
    await test_session.commit()
    return u
