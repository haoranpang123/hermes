# 河大家教小程序 - 前端项目

> UniApp + uView UI 微信小程序 MVP P0 阶段

## 项目简介

河大家教是一款专注于大学生家教撮合交易的微信小程序平台。本项目为 MVP P0 阶段前端实现，包含家长端和教师端所有核心页面。

## 技术栈

- **框架**：UniApp (Vue 3)
- **UI组件库**：uView UI 2.x
- **目标平台**：微信小程序 (mp-weixin)
- **样式预处理**：SCSS

## 目录结构

```
miniprogram/
├── App.vue                    # 应用入口
├── main.js                    # 入口文件，挂载 uView UI
├── manifest.json              # 应用配置
├── pages.json                 # 页面路由 & TabBar 配置
├── uni.scss                   # Design Token & 全局样式变量
├── package.json               # 依赖配置
├── README.md                  # 本文件
├── common/
│   └── mock.js                # 模拟数据（后续替换为真实API）
├── pages/
│   ├── login/
│   │   └── index.vue          # 登录页（微信登录+手机绑定+身份选择）
│   ├── index/
│   │   └── index.vue          # 首页（搜索+筛选+教师列表）
│   ├── teacher/
│   │   ├── detail.vue         # 教师详情页
│   │   ├── apply.vue          # 教师入驻申请
│   │   ├── status.vue         # 审核状态
│   │   ├── orders.vue         # 教师订单列表
│   │   ├── order-detail.vue   # 教师订单详情
│   │   └── income.vue         # 收入管理
│   ├── order/
│   │   ├── create.vue         # 下单支付页
│   │   ├── list.vue           # 订单列表（Tab切换）
│   │   └── detail.vue         # 订单详情（时间线+操作）
│   ├── wallet/
│   │   └── index.vue          # 虚拟币钱包
│   └── mine/
│       └── index.vue          # 个人中心
└── static/
    └── icons/                 # TabBar图标（需自行准备）
```

## 页面清单（MVP P0）

### 家长端（7个）
| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | pages/index/index | 搜索栏+筛选（科目/年级/地区）+教师卡片列表，下拉刷新+上拉加载 |
| 教师详情 | pages/teacher/detail | 头像+信息+科目标签+简介+资质+时间+评价+收藏/联系/预约 |
| 下单支付 | pages/order/create | 确认信息+金额汇总+微信支付按钮 |
| 订单列表 | pages/order/list | Tab切换（全部/待确认/进行中/待结算/已完成/已取消） |
| 订单详情 | pages/order/detail | 状态时间线+订单信息+动态操作按钮 |
| 虚拟币钱包 | pages/wallet/index | 余额卡片+充值套餐+消费记录 |
| 个人中心 | pages/mine/index | 头像昵称+菜单（订单/收藏/钱包/资料/设置） |

### 教师端（5个）
| 页面 | 路径 | 说明 |
|------|------|------|
| 入驻申请 | pages/teacher/apply | 表单（姓名/性别/学校/专业/科目/课时费/区域/简介/证件上传） |
| 审核状态 | pages/teacher/status | 待审核/已通过/已驳回三种状态展示 |
| 教师订单 | pages/teacher/orders | Tab切换+接单/拒绝/标记上课/标记完成操作 |
| 订单详情 | pages/teacher/order-detail | 确认接单/拒绝/标记上课/标记完成按钮 |
| 收入管理 | pages/teacher/income | 可提现余额+累计收入+提现+收入明细 |

### 通用页面（1个）
| 页面 | 路径 | 说明 |
|------|------|------|
| 登录页 | pages/login/index | 微信一键登录+手机号绑定+身份选择 |

## 设计规范

严格遵循 `docs/prototype/design-spec.md` 的设计规范：

- **主色**：#07C160（微信绿）
- **危险色**：#EE0A24
- **卡片**：圆角12px，阴影 0 2px 12px rgba(0,0,0,0.08)
- **按钮**：圆角8px，高度44px
- **字体**：-apple-system, PingFang SC
- **字号**：XXL 20px / XL 18px / LG 16px / MD 14px / SM 12px / XS 10px
- **金额**：#EE0A24 色

## 快速开始

### 1. 环境准备

```bash
# 安装 Node.js (>= 16)
# 安装 HBuilderX（推荐）或使用 CLI

# 全局安装 @dcloudio/uni-app CLI（可选）
npm install -g @dcloudio/uni-app
```

### 2. 安装依赖

```bash
cd ~/tutor-miniprogram/miniprogram
npm install
```

### 3. 配置 uView UI

如果 uView UI 没有正确安装，手动执行：

```bash
npm install uview-ui@2.0.36
```

确保 `main.js` 中已引入 uView UI，`uni.scss` 中已引入 `uview-ui/theme.scss`。

### 4. 准备 TabBar 图标

TabBar 图标需要放置在 `static/icons/` 目录下：

```
static/icons/
├── home.png
├── home-active.png
├── order.png
├── order-active.png
├── mine.png
└── mine-active.png
```

图标要求：81px × 81px，PNG格式，单色。

> 可使用 uView UI 内置图标或自行设计，然后在 `pages.json` 的 `tabBar.list` 中配置。

### 5. 启动开发

**方式一：使用 HBuilderX（推荐）**

1. 打开 HBuilderX
2. 文件 → 导入 → 从本地目录导入 → 选择 `~/tutor-miniprogram/miniprogram`
3. 运行 → 运行到小程序模拟器 → 微信开发者工具

**方式二：使用 CLI**

```bash
# 开发模式（编译到微信小程序）
npm run dev:mp-weixin

# 然后在微信开发者工具中打开 dist/dev/mp-weixin 目录
```

### 6. 配置微信小程序 AppID

在 `manifest.json` 中修改：

```json
"mp-weixin": {
  "appid": "你的微信小程序AppID"
}
```

## 模拟数据

所有页面的数据均来自 `common/mock.js`，包含：

- 教师列表（5位模拟教师）
- 教师详情（含简介、证书、时间、评价）
- 订单列表（各状态示例）
- 虚拟币钱包（余额、交易流水）
- 收入明细
- 筛选选项

后续联调时，将 `mock.js` 中的数据引用替换为真实 API 调用即可。

API 接口文档：`~/tutor-miniprogram/backend/docs/api-design.md`

## 页面流转关系

```
登录页 → 身份选择
  ├─ 家长 → 首页Tab
  │   ├─ 首页 → 教师详情 → 下单支付 → 订单列表
  │   ├─ 订单Tab → 订单列表 → 订单详情
  │   └─ 我的Tab → 个人中心 → 钱包/收藏/资料
  └─ 教师 → 入驻申请 → 审核状态
      ├─ 审核通过 → 教师订单 → 订单详情
      └─ 收入管理
```

## 后续工作

- [ ] 接入真实微信登录（wx.login + 后端JWT）
- [ ] 接入微信支付
- [ ] 替换模拟数据为 API 调用
- [ ] 实现P1功能（聊天、评价、日历、通知等）
- [ ] 性能优化和代码分包
- [ ] 配置正式环境域名和AppID
