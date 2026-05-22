# 河大家教小程序 — API 接口设计文档

> **版本**: v1.0
> **日期**: 2026-05-23
> **作者**: 小C（后端开发工程师）
> **Base URL**: `https://api.henututor.cn/api/v1`
> **认证方案**: JWT Bearer Token (微信登录签发)
> **数据格式**: JSON

---

## 一、统一规范

### 1.1 统一响应格式

所有API返回统一的JSON结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": { }
}
```

| code | 含义 | 说明 |
|------|------|------|
| 0 | 成功 | 请求正常处理 |
| 1001 | 参数错误 | 请求参数校验失败 |
| 1002 | 未登录 | 缺少或无效的JWT Token |
| 1003 | 无权限 | 角色不匹配或资源无权限 |
| 1004 | 资源不存在 | 请求的数据不存在 |
| 1005 | 业务规则限制 | 触发业务规则约束(如余额不足、状态不允许) |
| 2001 | 微信接口错误 | 调用微信API失败 |
| 2002 | 微信支付错误 | 支付相关错误 |
| 5000 | 服务器内部错误 | 未知错误 |

分页响应格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 1.2 认证要求

```
Authorization: Bearer <JWT_TOKEN>
```

- 公开接口：`PUBLIC` — 无需认证
- 家长端接口：`PARENT` — 需JWT + role=parent
- 教师端接口：`TEACHER` — 需JWT + role=teacher + audit_status=approved
- 管理后台接口：`ADMIN` — 需JWT + role=admin

### 1.3 请求头

```
Content-Type: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>          # 请求追踪ID（可选）
```

---

## 二、微信登录认证流程

### 2.1 流程图

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ 小程序端  │     │  后端API  │     │ 微信服务  │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                 │               │
     │ 1. wx.login()   │               │
     │─────────────────────────────────▶
     │                 │               │
     │ 2. 返回 code    │               │
     │◀─────────────────────────────────
     │                 │               │
     │ 3. POST /auth/login              │
     │    { code }      │               │
     │────────────────▶ │               │
     │                 │ 4. code2session│
     │                 │───────────────▶
     │                 │ 5. openid,     │
     │                 │    session_key │
     │                 │◀───────────────
     │                 │               │
     │                 │ 6. 查询/创建用户│
     │                 │ 7. 签发JWT     │
     │                 │               │
     │ 8. { token,      │               │
     │    user_info,     │               │
     │    is_new }      │               │
     │◀──────────────── │               │
     │                 │               │
     │ 9. wx.getPhoneNumber            │
     │─────────────────────────────────▶
     │ 10. 返回加密手机号               │
     │◀─────────────────────────────────
     │                 │               │
     │ 11. POST /auth/bind-phone       │
     │     { code }     │               │
     │────────────────▶ │               │
     │                 │ 12. 解密手机号  │
     │                 │ 13. 绑定手机号  │
     │ 14. { phone }    │               │
     │◀──────────────── │               │
     │                 │               │
     │ 15. POST /auth/select-role      │
     │     { role }     │               │
     │────────────────▶ │               │
     │ 16. { user_info }│               │
     │◀────────────────
```

### 2.2 JWT Token 设计

```json
{
  "sub": "<user_id>",
  "role": "parent|teacher|admin",
  "iat": 1716422400,
  "exp": 1716508800,
  "jti": "<uuid>"
}
```

- 过期时间：24小时
- 刷新策略：每次请求时若 token 有效期剩余 < 12h，响应头返回新 token
- 存储方式：小程序端存储在本地 Storage

---

## 三、API 接口清单

### 3.1 认证模块 (`/auth`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 1 | POST | `/auth/login` | 微信登录(用code换取token) | PUBLIC | P0 |
| 2 | POST | `/auth/bind-phone` | 绑定手机号 | PARENT/TEACHER | P0 |
| 3 | POST | `/auth/select-role` | 选择身份(role只能选一次) | PARENT/TEACHER | P0 |
| 4 | GET | `/auth/profile` | 获取当前用户信息 | PARENT/TEACHER/ADMIN | P0 |
| 5 | PUT | `/auth/profile` | 更新用户信息(头像/昵称) | PARENT/TEACHER/ADMIN | P0 |
| 6 | POST | `/auth/refresh` | 刷新Token | PARENT/TEACHER/ADMIN | P0 |

#### POST `/auth/login`

```json
// Request
{
  "code": "0d3XXxGa1ZCD1u0OKOJa1N3TXY1XXxG3"
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user_info": {
      "user_id": 1,
      "nickname": "微信用户",
      "avatar_url": "https://thirdwx.qlogo.cn/...",
      "phone": null,
      "role": null,
      "has_selected_role": false
    },
    "is_new": true
  }
}
```

#### POST `/auth/bind-phone`

```json
// Request
{
  "code": "wx_phone_code_from_getPhoneNumber"
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "phone": "138****1234"
  }
}
```

#### POST `/auth/select-role`

```json
// Request
{
  "role": "parent"
}

// Response (家长)
{
  "code": 0,
  "message": "ok",
  "data": {
    "user_id": 1,
    "role": "parent",
    "need_teacher_apply": false
  }
}

// Response (教师)
{
  "code": 0,
  "message": "ok",
  "data": {
    "user_id": 1,
    "role": "teacher",
    "need_teacher_apply": true
  }
}
```

---

### 3.2 教师端 — 入驻与资料 (`/teacher`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 7 | POST | `/teacher/apply` | 提交入驻申请 | TEACHER | P0 |
| 8 | GET | `/teacher/status` | 查询审核状态 | TEACHER | P0 |
| 9 | PUT | `/teacher/profile` | 修改教师资料(审核通过后) | TEACHER | P0 |
| 10 | GET | `/teacher/profile` | 获取教师自己的完整资料 | TEACHER | P0 |
| 11 | POST | `/teacher/certificate` | 上传资质证书 | TEACHER | P0 |
| 12 | DELETE | `/teacher/certificate/{cert_id}` | 删除资质证书 | TEACHER | P0 |
| 13 | PUT | `/teacher/subjects` | 设置教学科目与价格 | TEACHER | P0 |
| 14 | GET | `/teacher/subjects` | 获取教学科目列表 | TEACHER | P0 |
| 15 | PUT | `/teacher/schedules` | 设置可授课时间 | TEACHER | P0 |
| 16 | GET | `/teacher/schedules` | 获取可授课时间 | TEACHER | P0 |
| 17 | GET | `/teacher/income` | 收入概览(余额/累计) | TEACHER | P0 |
| 18 | GET | `/teacher/income/records` | 收入明细列表 | TEACHER | P0 |
| 19 | POST | `/teacher/withdraw` | 申请提现 | TEACHER | P0 |

#### POST `/teacher/apply`

```json
// Request
{
  "real_name": "张三",
  "gender": "male",
  "university": "河南大学",
  "major": "数学与应用数学",
  "grade": "大三",
  "bio": "两年家教经验，曾辅导多名初中生数学...",
  "min_price": 80,
  "teaching_regions": ["龙亭区", "金明区"],
  "subjects": [
    { "subject": "math", "grade_level": "junior_1", "unit_price": 80 },
    { "subject": "math", "grade_level": "junior_2", "unit_price": 80 }
  ],
  "schedules": [
    { "day_of_week": 1, "start_time": "18:00", "end_time": "20:00" },
    { "day_of_week": 3, "start_time": "19:00", "end_time": "21:00" }
  ],
  "certificates": [
    { "cert_type": "student_card", "image_url": "https://..." },
    { "cert_type": "other", "image_url": "https://..." }
  ]
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "teacher_id": 1,
    "audit_status": "pending"
  }
}
```

---

### 3.3 家长端 — 教师浏览 (`/teachers` — 公开)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 20 | GET | `/teachers` | 教师列表(搜索+筛选+分页) | PUBLIC | P0 |
| 21 | GET | `/teachers/{teacher_id}` | 教师详情 | PUBLIC | P0 |
| 22 | POST | `/teachers/{teacher_id}/contact` | 消耗虚拟币查看联系方式 | PARENT | P0 |
| 23 | POST | `/teachers/{teacher_id}/favorite` | 收藏教师 | PARENT | P0 |
| 24 | DELETE | `/teachers/{teacher_id}/favorite` | 取消收藏 | PARENT | P0 |
| 25 | GET | `/teachers/favorites` | 我的收藏列表 | PARENT | P0 |

#### GET `/teachers`

```json
// Query Params
{
  "keyword": "数学",           // 搜索关键词(教师名/科目名)
  "subjects": "math,english", // 科目筛选, 逗号分隔
  "grade_level": "junior_1",  // 年级筛选
  "region": "龙亭区",         // 区域筛选
  "gender": "male",           // 性别筛选 (P1)
  "min_price": 50,            // 最低价格
  "max_price": 120,           // 最高价格
  "sort": "rating",           // 排序: rating=综合, price_asc/desc
  "page": 1,
  "page_size": 20
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [
      {
        "teacher_id": 1,
        "nickname": "数学张老师",
        "avatar_url": "https://...",
        "university": "河南大学",
        "major": "数学与统计学院",
        "grade": "大三",
        "subjects": ["初中数学", "初中物理"],
        "min_price": 80,
        "avg_rating": 4.8,
        "review_count": 128,
        "is_available": true,
        "teaching_regions": ["龙亭区", "金明区"]
      }
    ],
    "total": 56,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

#### GET `/teachers/{teacher_id}`

```json
// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "teacher_id": 1,
    "nickname": "数学张老师",
    "avatar_url": "https://...",
    "real_name": "张三",
    "gender": "male",
    "university": "河南大学",
    "major": "数学与统计学院",
    "grade": "大三",
    "bio": "两年家教经验...",
    "min_price": 80,
    "avg_rating": 4.8,
    "review_count": 128,
    "is_available": true,
    "teaching_regions": ["龙亭区", "金明区"],
    "certificates": [
      { "cert_type": "student_card", "image_url": "https://..." }
    ],
    "subjects": [
      { "subject": "math", "grade_level": "junior_1", "unit_price": 80 }
    ],
    "schedules": [
      { "day_of_week": 1, "start_time": "18:00", "end_time": "20:00", "status": "available" }
    ],
    "reviews": [
      {
        "parent_nickname": "家***长",
        "teaching_ability": 5,
        "communication": 5,
        "punctuality": 4,
        "content": "老师很耐心...",
        "created_at": "2026-05-20 10:30:00"
      }
    ],
    "contact_viewed": false,
    "contact_expire_at": null,
    "is_favorited": false
  }
}
```

#### POST `/teachers/{teacher_id}/contact`

```json
// Request (可选，仅当需要指定科目计费时)
{
  "subject": "math"
}

// Response (成功)
{
  "code": 0,
  "message": "ok",
  "data": {
    "phone": "138****1234",
    "wechat": null,
    "consumed_coins": 5,
    "balance_after": 30,
    "expire_at": "2026-05-30 12:25:00"
  }
}

// Response (余额不足)
{
  "code": 1005,
  "message": "虚拟币余额不足，当前余额3币，需要5币",
  "data": {
    "current_balance": 3,
    "required": 5,
    "shortage": 2
  }
}

// Response (7天内已查看，不重复扣费)
{
  "code": 0,
  "message": "ok",
  "data": {
    "phone": "138****1234",
    "consumed_coins": 0,
    "balance_after": 35,
    "expire_at": "2026-05-30 12:25:00"
  }
}
```

---

### 3.4 订单模块 (`/orders`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 26 | POST | `/orders` | 创建订单(家长下单) | PARENT | P0 |
| 27 | GET | `/orders` | 订单列表(按角色+状态) | PARENT/TEACHER | P0 |
| 28 | GET | `/orders/{order_id}` | 订单详情 | PARENT/TEACHER | P0 |
| 29 | POST | `/orders/{order_id}/accept` | 教师确认接单 | TEACHER | P0 |
| 30 | POST | `/orders/{order_id}/reject` | 教师拒绝接单 | TEACHER | P0 |
| 31 | POST | `/orders/{order_id}/start` | 教师标记已上课 | TEACHER | P0 |
| 32 | POST | `/orders/{order_id}/complete` | 教师标记完成 | TEACHER | P0 |
| 33 | POST | `/orders/{order_id}/confirm` | 家长确认完成 | PARENT | P0 |
| 34 | POST | `/orders/{order_id}/refund` | 家长申请退款(P1) | PARENT | P1 |
| 35 | POST | `/orders/{order_id}/cancel` | 管理员取消订单并退款 | ADMIN | P0 |
| 36 | GET | `/orders/{order_id}/timeline` | 订单状态时间线 | PARENT/TEACHER | P0 |

#### POST `/orders`

```json
// Request
{
  "teacher_id": 1,
  "subject": "math",
  "grade": "junior_1",
  "lesson_date": "2026-05-30",
  "start_time": "09:00",
  "end_time": "11:00",
  "address": "龙亭区XX小区"
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "order_id": 100,
    "order_no": "HD20260523100001",
    "total_amount": 160.00,
    "wechat_pay_params": {
      "appId": "wxXXX",
      "timeStamp": "1716422400",
      "nonceStr": "abc123",
      "package": "prepay_id=wxXXX",
      "signType": "RSA",
      "paySign": "..."
    }
  }
}
```

#### POST `/orders/{order_id}/accept` (教师确认接单)

```json
// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "order_id": 100,
    "status": "pending_trial",
    "accepted_at": "2026-05-23 12:30:00"
  }
}
```

#### POST `/orders/{order_id}/confirm` (家长确认完成)

```json
// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "order_id": 100,
    "status": "completed",
    "total_amount": 160.00,
    "commission_amount": 24.00,
    "settlement_amount": 136.00
  }
}
```

---

### 3.5 虚拟币钱包 (`/wallet`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 37 | GET | `/wallet` | 钱包余额与概览 | PARENT | P0 |
| 38 | GET | `/wallet/transactions` | 交易流水列表 | PARENT | P0 |
| 39 | POST | `/wallet/recharge` | 创建充值订单(微信支付) | PARENT | P0 |

#### GET `/wallet`

```json
// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "balance": 35,
    "total_recharged": 50,
    "total_spent": 15
  }
}
```

#### POST `/wallet/recharge`

```json
// Request
{
  "amount": 10
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "recharge_id": 200,
    "amount": 10,
    "coins": 10,
    "wechat_pay_params": {
      "appId": "wxXXX",
      "timeStamp": "1716422400",
      "nonceStr": "abc123",
      "package": "prepay_id=wxXXX",
      "signType": "RSA",
      "paySign": "..."
    }
  }
}
```

---

### 3.6 需求发布 (`/demands`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 40 | POST | `/demands` | 发布需求 | PARENT | P0 |
| 41 | GET | `/demands` | 我的需求列表 | PARENT | P0 |
| 42 | GET | `/demands/{demand_id}` | 需求详情 | PARENT | P0 |
| 43 | PUT | `/demands/{demand_id}` | 修改需求 | PARENT | P0 |
| 44 | DELETE | `/demands/{demand_id}` | 关闭需求 | PARENT | P0 |

---

### 3.7 评价模块 (`/reviews`) — P1

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 45 | POST | `/reviews` | 提交评价 | PARENT | P1 |
| 46 | GET | `/teachers/{teacher_id}/reviews` | 查看教师评价列表 | PUBLIC | P1 |

---

### 3.8 管理后台 (`/admin`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 47 | POST | `/admin/login` | 管理后台登录(账号密码) | PUBLIC | P0 |
| 48 | GET | `/admin/dashboard` | 数据看板 | ADMIN | P1 |
| 49 | GET | `/admin/users` | 用户列表 | ADMIN | P0 |
| 50 | PUT | `/admin/users/{user_id}/status` | 启用/禁用用户 | ADMIN | P0 |
| 51 | GET | `/admin/teachers/pending` | 待审核教师列表 | ADMIN | P0 |
| 52 | GET | `/admin/teachers/{teacher_id}` | 教师审核详情 | ADMIN | P0 |
| 53 | POST | `/admin/teachers/{teacher_id}/approve` | 审核通过 | ADMIN | P0 |
| 54 | POST | `/admin/teachers/{teacher_id}/reject` | 审核驳回 | ADMIN | P0 |
| 55 | GET | `/admin/orders` | 订单列表 | ADMIN | P0 |
| 56 | GET | `/admin/orders/{order_id}` | 订单详情(含操作日志) | ADMIN | P0 |
| 57 | POST | `/admin/orders/{order_id}/refund` | 管理员退款 | ADMIN | P0 |
| 58 | GET | `/admin/wallet/transactions` | 虚拟币流水 | ADMIN | P0 |
| 59 | GET | `/admin/commissions` | 佣金明细 | ADMIN | P0 |
| 60 | GET | `/admin/withdrawals` | 提现申请列表 | ADMIN | P0 |
| 61 | POST | `/admin/withdrawals/{withdrawal_id}/approve` | 通过提现申请 | ADMIN | P0 |
| 62 | POST | `/admin/withdrawals/{withdrawal_id}/reject` | 驳回提现申请 | ADMIN | P0 |
| 63 | GET | `/admin/configs` | 获取系统配置 | ADMIN | P0 |
| 64 | PUT | `/admin/configs/{config_key}` | 修改系统配置 | ADMIN | P0 |

#### POST `/admin/login`

```json
// Request
{
  "username": "admin",
  "password": "secure_password"
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "admin_info": {
      "admin_id": 1,
      "username": "admin",
      "real_name": "超级管理员"
    }
  }
}
```

#### POST `/admin/teachers/{teacher_id}/approve`

```json
// Response
{
  "code": 0,
  "message": "审核通过",
  "data": {
    "teacher_id": 1,
    "audit_status": "approved",
    "audited_at": "2026-05-23 14:00:00"
  }
}
```

#### POST `/admin/teachers/{teacher_id}/reject`

```json
// Request
{
  "reason": "学生证照片模糊，请重新上传"
}

// Response
{
  "code": 0,
  "message": "已驳回",
  "data": {
    "teacher_id": 1,
    "audit_status": "rejected",
    "audit_reason": "学生证照片模糊，请重新上传",
    "audited_at": "2026-05-23 14:00:00"
  }
}
```

---

### 3.9 微信支付回调 (`/callback`) — 公开

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 65 | POST | `/callback/wxpay/order` | 订单支付回调 | PUBLIC(签名验证) | P0 |
| 66 | POST | `/callback/wxpay/recharge` | 充值支付回调 | PUBLIC(签名验证) | P0 |
| 67 | POST | `/callback/wxpay/refund` | 退款回调 | PUBLIC(签名验证) | P0 |

---

### 3.10 文件上传 (`/upload`)

| 序号 | 方法 | 路径 | 说明 | 认证 | 优先级 |
|------|------|------|------|------|--------|
| 68 | POST | `/upload/image` | 上传图片(证书/头像等) | PARENT/TEACHER | P0 |

---

## 四、关键接口详解

### 4.1 微信支付回调处理

#### POST `/callback/wxpay/order` — 订单支付回调

```
处理流程:
1. 验证签名 (微信支付V3 API: 证书+签名验证)
2. 解密回调数据 (AES-256-GCM)
3. 根据 out_trade_no 查找订单
4. 更新订单状态: pay_transaction_id, paid_at
5. 创建教师接单通知
6. 返回 HTTP 200 + {"code": "SUCCESS"}

错误处理:
- 签名验证失败 → HTTP 401
- 订单不存在 → 记录日志, 返回 SUCCESS (防重复回调)
- 订单状态异常 → 记录日志, 告警, 返回 SUCCESS
```

#### POST `/callback/wxpay/recharge` — 充值支付回调

```
处理流程:
1. 验证签名
2. 解密数据
3. 查找充值记录, 幂等校验
4. 开启事务:
   a. SELECT wallet WHERE user_id FOR UPDATE
   b. UPDATE wallet SET balance = balance + coins, total_recharged += coins
   c. INSERT wallet_transactions (type=recharge)
   d. UPDATE 充值记录状态 = paid
5. 返回 SUCCESS
```

### 4.2 虚拟币扣减 (查看联系方式)

```
POST /teachers/{teacher_id}/contact

处理流程:
1. 校验JWT, role=parent
2. 查询教师是否存在且审核通过
3. 查询 contact_view 记录, 检查7天内是否已查看:
   - 如果7天内有记录且未过期 → 直接返回, consumed_coins=0
4. 获取虚拟币价格(MVP: system_configs.contact_coin_price = 5)
5. 开启事务:
   a. SELECT wallet WHERE user_id FOR UPDATE  (行锁)
   b. 检查 balance >= price
   c. UPDATE wallet SET balance = balance - price, total_spent += price
   d. INSERT wallet_transactions (type=consume, ref_id=teacher_id, ref_type=teacher)
   e. INSERT/UPDATE contact_view 记录
6. 返回教师联系方式(phone脱敏)
7. 提交事务

并发安全:
- 使用 SELECT ... FOR UPDATE 行锁
- 使用唯一索引 uk_parent_teacher 防止重复扣费
```

### 4.3 订单状态流转

```
完整状态流转控制:

[parent] POST /orders              → status=pending_confirm, 生成微信支付参数
[callback] 微信支付成功回调          → 记录paid_at
[teacher] POST /orders/{id}/accept  → status=pending_trial, teacher_accepted_at
  - 校验: 订单状态=pending_confirm
  - 校验: 教师=订单的teacher_id
  - 校验: 未超过24h

[teacher] POST /orders/{id}/reject  → status=cancelled
  - 校验: 订单状态=pending_confirm
  - 校验: 填写拒绝原因
  - 触发: 微信退款

[system] 定时任务: 24h超时自动取消   → status=cancelled, 触发退款

[teacher] POST /orders/{id}/start   → status=in_progress
  - 校验: 订单状态=pending_trial

[teacher] POST /orders/{id}/complete → status=pending_settlement
  - 校验: 订单状态=in_progress
  - 设置: auto_confirm_deadline = NOW() + 48h

[parent] POST /orders/{id}/confirm  → status=completed
  - 校验: 订单状态=pending_settlement
  - 计算: commission_amount, settlement_amount
  - 结算: 教师收入记录写入
  - 解锁: 关联的排课时段

[parent] POST /orders/{id}/refund   → status=dispute (P1)
[system] 定时任务: 48h自动确认      → status=completed (同confirm逻辑)
[admin] POST /orders/{id}/refund    → status=cancelled, 触发退款
```

### 4.4 提现流程

```
POST /teacher/withdraw

处理流程:
1. 校验最低提现金额 (system_configs.min_withdrawal_amount, 默认¥10)
2. 查询教师可提现余额:
   可提现 = SUM(已完成订单结算金额) - SUM(已提现金额)
3. 校验: 提现金额 ≤ 可提现余额
4. 创建 withdrawal_requests (status=pending)
5. 管理后台审核

管理后台:
POST /admin/withdrawals/{id}/approve:
  → status=approved, 触发企业付款到零钱
  → 企业付款成功后: status=paid, wx_transfer_id, paid_at

POST /admin/withdrawals/{id}/reject:
  → status=rejected, audit_reason
```

---

## 五、P1 功能 API（标注，不做完整设计）

以下API在MVP Phase 1后实现，此处仅列出：

| 序号 | 方法 | 路径 | 说明 | 优先级 |
|------|------|------|------|--------|
| P1-1 | POST | `/reviews` | 家长提交评价 | P1 |
| P1-2 | GET | `/teachers/{id}/reviews` | 教师评价列表 | P1 |
| P1-3 | GET | `/chat/rooms` | 聊天会话列表(腾讯云IM) | P1 |
| P1-4 | POST | `/chat/token` | 获取IM UserSig | P1 |
| P1-5 | GET | `/teachers/{id}/calendar` | 教师日历视图 | P1 |
| P1-6 | GET | `/wallet/recharge/packages` | 充值套餐列表(含赠送) | P1 |
| P1-7 | GET | `/home/banners` | 首页轮播图 | P1 |
| P1-8 | GET | `/home/notices` | 系统公告 | P1 |

---

> **文档状态**: V1.0 完成
> **下一步**: 技术选型确认 → 模型代码实现 → 接口开发
