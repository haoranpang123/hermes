# 河大家教小程序 — 技术选型确认文档

> **版本**: v1.0
> **日期**: 2026-05-23
> **作者**: 小C（后端开发工程师）
> **状态**: 已确认

---

## 一、技术选型总览

### 1.1 核心框架

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| **Python** | 3.10+ | 后端开发语言 | 团队熟悉，生态丰富，异步支持好 |
| **FastAPI** | 0.100+ | Web框架 | 高性能异步框架，自动生成 OpenAPI 文档，Pydantic 类型校验 |
| **SQLAlchemy** | 2.0+ | ORM | 异步支持(2.0 asyncio)，成熟稳定，社区活跃 |
| **Alembic** | 1.12+ | 数据库迁移 | SQLAlchemy 官方迁移工具，支持自动生成迁移脚本 |
| **Pydantic** | 2.0+ | 数据校验 | FastAPI 内置，类型安全，性能优秀 |

### 1.2 数据库

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| **MySQL** | 8.0 | 主数据库 | 事务支持完善(ACID)，读取性能好，运维成熟 |
| **Redis** | 7.0+ | 缓存/队列 | JWT黑名单、短信限流、定时任务锁、会话缓存 |

### 1.3 第三方服务

| 服务 | 用途 | 阶段 | 说明 |
|------|------|------|------|
| **微信小程序登录** | 用户认证 | P0 | code → openid + session_key |
| **微信手机号组件** | 手机号绑定 | P0 | getPhoneNumber 解密 |
| **微信支付 V3 API** | 订单支付、充值、退款、企业付款 | P0 | RSA签名，AES解密回调 |
| **腾讯云 IM** | 一对一聊天 | P1 | UserSig生成，REST API管理 |
| **腾讯云 COS** | 图片/文件存储 | P0 | 证书上传，头像存储 |

### 1.4 部署与运维

| 技术 | 用途 |
|------|------|
| **Docker** | 容器化部署 |
| **Nginx** | 反向代理 + SSL终止 |
| **Supervisor / systemd** | 进程管理 |
| **Celery + Redis** | 异步任务(P1阶段) |

---

## 二、核心依赖清单

### 2.1 requirements.txt

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy[asyncio]==2.0.23
aiomysql==0.2.0
alembic==1.13.0

# Data Validation
pydantic==2.5.2
pydantic-settings==2.1.0

# Authentication
PyJWT==2.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# WeChat
wechatpayv3==1.2.10       # 微信支付 V3
cryptography==41.0.7       # 微信回调解密

# Redis
redis==5.0.1
hiredis==2.2.3            # Redis 高性能解析器

# HTTP Client
httpx==0.25.2             # 异步HTTP客户端(调用微信API)

# Image/File Upload
python-multipart==0.0.6   # 文件上传支持
Pillow==10.1.0            # 图片处理(压缩/缩略图)

# Tencent Cloud (P1阶段)
tencentcloud-sdk-python==3.0.1061  # 腾讯云IM/COS

# Task Queue (P1阶段)
celery==5.3.4

# Utilities
python-dotenv==1.0.0
loguru==0.7.2             # 结构化日志
orjson==3.9.10            # 高性能JSON序列化
```

---

## 三、项目目录结构

```
~/tutor-miniprogram/backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理(Settings)
│   ├── dependencies.py           # FastAPI 依赖注入
│   │
│   ├── api/                      # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # 路由汇总
│   │   │   ├── auth.py           # 认证相关API
│   │   │   ├── teachers.py       # 教师浏览API
│   │   │   ├── teacher.py        # 教师入驻/资料API
│   │   │   ├── orders.py         # 订单API
│   │   │   ├── wallet.py         # 钱包API
│   │   │   ├── demands.py        # 需求发布API
│   │   │   ├── reviews.py        # 评价API (P1)
│   │   │   ├── upload.py         # 文件上传API
│   │   │   ├── callback.py       # 微信支付回调API
│   │   │   └── admin/            # 管理后台API
│   │   │       ├── __init__.py
│   │   │       ├── auth.py       # 后台登录
│   │   │       ├── users.py      # 用户管理
│   │   │       ├── teachers.py   # 教师审核
│   │   │       ├── orders.py     # 订单管理
│   │   │       ├── finance.py    # 财务管理
│   │   │       └── config.py     # 系统配置
│   │   └── deps/                 # 接口级依赖(认证守卫等)
│   │       ├── __init__.py
│   │       ├── auth.py           # get_current_user / require_role
│   │       └── pagination.py     # 分页参数
│   │
│   ├── models/                   # SQLAlchemy 数据模型
│   │   ├── __init__.py           # 模型汇总 + Base
│   │   ├── user.py
│   │   ├── teacher.py
│   │   ├── order.py
│   │   ├── wallet.py
│   │   ├── review.py
│   │   ├── demand.py
│   │   ├── favorite.py
│   │   ├── withdrawal.py
│   │   └── system_config.py
│   │
│   ├── schemas/                  # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── teacher.py
│   │   ├── order.py
│   │   ├── wallet.py
│   │   ├── demand.py
│   │   ├── review.py
│   │   └── common.py             # 通用响应/分页模型
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py       # 登录认证逻辑
│   │   ├── teacher_service.py    # 教师入驻/审核逻辑
│   │   ├── order_service.py      # 订单状态机/结算逻辑
│   │   ├── wallet_service.py     # 钱包/虚拟币扣减逻辑
│   │   ├── demand_service.py     # 需求发布逻辑
│   │   ├── review_service.py     # 评价逻辑 (P1)
│   │   ├── notification_service.py # 通知服务 (P1)
│   │   └── payment_service.py    # 微信支付封装
│   │
│   ├── core/                     # 核心基础设施
│   │   ├── __init__.py
│   │   ├── database.py           # 数据库引擎 + Session工厂
│   │   ├── redis.py              # Redis 连接池
│   │   ├── security.py           # JWT签发/验证/密码哈希
│   │   ├── wechat.py             # 微信API封装(登录/支付/手机号)
│   │   └── exceptions.py         # 自定义异常类
│   │
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── id_generator.py       # 订单号/流水号生成器
│       ├── phone_mask.py         # 手机号脱敏
│       └── image_processor.py    # 图片压缩/验证
│
├── migrations/                   # Alembic 迁移脚本
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures
│   ├── test_auth.py
│   ├── test_teacher.py
│   ├── test_orders.py
│   └── test_wallet.py
│
├── docs/                         # 技术文档
│   ├── database-design.md
│   ├── api-design.md
│   └── tech-stack.md
│
├── scripts/                      # 运维脚本
│   ├── init_db.sql               # 初始化建表SQL
│   └── seed_data.py              # 测试数据填充
│
├── .env.example                  # 环境变量模板
├── .env                          # 环境变量(不提交Git)
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 四、核心模块设计思路

### 4.1 配置管理 (app/config.py)

使用 `pydantic-settings` 从环境变量读取配置：

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "河大家教"
    DEBUG: bool = False
    SECRET_KEY: str

    # Database
    DATABASE_URL: str = "mysql+aiomysql://user:pass@localhost:3306/henu_tutor"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # WeChat Mini Program
    WX_APP_ID: str
    WX_APP_SECRET: str

    # WeChat Pay V3
    WXPAY_MCH_ID: str
    WXPAY_API_V3_KEY: str
    WXPAY_SERIAL_NO: str
    WXPAY_PRIVATE_KEY_PATH: str
    WXPAY_NOTIFY_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # Tencent Cloud (P1)
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_IM_SDK_APP_ID: str = ""

    class Config:
        env_file = ".env"
```

### 4.2 数据库会话管理 (app/core/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

### 4.3 认证中间件 (app/api/deps/auth.py)

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    user = await db.get(User, payload["sub"])
    if not user or user.status == 0:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user

def require_role(role: str):
    async def dependency(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="无权限")
        return user
    return dependency
```

### 4.4 订单服务核心逻辑 (app/services/order_service.py)

```python
class OrderService:
    """订单服务 - 处理订单状态机所有流转"""

    async def create_order(self, parent_id, teacher_id, ...):
        """创建订单 + 生成微信支付参数"""

    async def handle_payment_callback(self, order_no, transaction_id):
        """处理微信支付成功回调"""

    async def teacher_accept(self, order_id, teacher_id):
        """教师确认接单: pending_confirm → pending_trial"""

    async def teacher_reject(self, order_id, teacher_id, reason):
        """教师拒绝: pending_confirm → cancelled + 退款"""

    async def teacher_start(self, order_id, teacher_id):
        """教师标记上课: pending_trial → in_progress"""

    async def teacher_complete(self, order_id, teacher_id):
        """教师标记完成: in_progress → pending_settlement"""

    async def parent_confirm(self, order_id, parent_id):
        """家长确认: pending_settlement → completed + 结算"""

    async def auto_confirm(self, order_id):
        """48h自动确认: 同parent_confirm"""

    async def auto_cancel_expired(self):
        """定时任务: 24h未接单自动取消"""
```

---

## 五、关键技术决策

### 5.1 为什么用异步 (async/await)

- FastAPI 原生异步支持，结合 aiomysql 实现非阻塞数据库操作
- 微信支付回调、多服务调用等IO密集场景下，异步可显著提升并发处理能力
- SQLAlchemy 2.0 提供完整的 async API

### 5.2 为什么MySQL而非PostgreSQL

- 团队 MySQL 运维经验丰富
- 小程序的读多写少场景 MySQL 完全够用
- 云服务商 MySQL 托管方案成熟且成本低

### 5.3 事务一致性保证

- 虚拟币扣减：`SELECT ... FOR UPDATE` 悲观锁 + 事务
- 订单结算：佣金扣除 + 教师余额增加在同一事务中
- 支付回调：幂等校验(transaction_id去重)

### 5.4 JWT vs Session

选择 JWT 的原因：
- 无状态，适合微服务扩展
- 小程序端存储方便
- Token 内嵌角色信息，减少数据库查询
- 配合 Redis 黑名单实现登出/封禁

---

## 六、MVP阶段简化事项

以下功能在MVP阶段简化处理：

| 原设计 | MVP简化 | 理由 |
|--------|---------|------|
| 教师日历组件 | 文本时间段描述 + teacher_schedules 表 | P1 再做日历 UI |
| 聊天(腾讯云IM) | 订单详情页展示脱敏手机号(需消耗虚拟币) | P1 接入 IM |
| 评价系统 | 表结构预留，API暂不开放 | P1 实现 |
| 充值赠送 | 固定 1:1 充值 | P1 增加赠送活动 |
| 虚拟币按科目差异化定价 | 统一5币 | MVP快速上线 |
| 微信服务通知 | 小程序内轮询 + 订单状态刷新 | P1 接入模板消息 |
| 轮播图/公告 | 前端硬编码占位 | P1 管理后台配置 |
| 数据看板 | 简单的 COUNT 查询 | P1 图表+趋势 |

---

> **文档状态**: V1.0 完成
> **下一步**: 开始 Phase 1 开发：用户系统 → 教师入驻 → 订单支付
