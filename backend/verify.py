"""后端代码验证脚本"""
import sys
sys.path.insert(0, '/home/ubuntu/tutor-miniprogram/backend')

print("=== 1. Models ===")
from app.models import Base
tables = sorted(Base.metadata.tables.keys())
print(f"  {len(tables)} tables: OK")
for t in tables:
    print(f"    - {t}")

print("\n=== 2. Core ===")
from app.config import get_settings
print(f"  Settings: OK (APP_NAME={get_settings().APP_NAME})")

from app.core.security import create_access_token, decode_access_token
token = create_access_token(1, "parent")
print(f"  JWT: OK (token={token[:30]}...)")

print("\n=== 3. Schemas ===")
from app.schemas.auth import LoginRequest, UserInfo
from app.schemas.teacher import TeacherApplyRequest
from app.schemas.order import CreateOrderRequest
from app.schemas.wallet import RechargeRequest
from app.schemas.common import APIResponse, paginate
print("  All schemas: OK")

print("\n=== 4. API Router ===")
from app.api.v1.router import v1_router
routes = [r.path for r in v1_router.routes]
print(f"  {len(routes)} routes registered")

print("\n=== 5. FastAPI App ===")
from app.main import app as fastapi_app
print(f"  App: {fastapi_app.title} v{fastapi_app.version}")

print("\n=== ALL CHECK PASSED ===")
