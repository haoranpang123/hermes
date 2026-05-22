/**
 * 河大家教小程序 — 模拟数据（Mock Data）
 * 后续联调时替换为真实 API 调用
 */

// ============================================================
// 家长用户信息
// ============================================================
export const mockParentUser = {
  user_id: 1,
  nickname: '小明家长',
  avatar_url: '/static/icons/default-avatar.png',
  phone: '138****5678',
  role: 'parent',
}

// ============================================================
// 教师用户信息（用于教师端）
// ============================================================
export const mockTeacherUser = {
  user_id: 2,
  nickname: '数学张老师',
  avatar_url: '/static/icons/default-avatar.png',
  phone: '139****1234',
  role: 'teacher',
}

// ============================================================
// 教师列表（首页搜索）
// ============================================================
export const mockTeachers = [
  {
    teacher_id: 1,
    nickname: '张明远',
    avatar_url: '',
    avatar_bg: 'linear-gradient(135deg, #FF6B6B, #EE5A24)',
    initial: '张',
    university: '河南大学',
    major: '数学与统计学院',
    grade: '大三',
    subjects: ['初中数学', '初中物理', '高中数学'],
    min_price: 80,
    avg_rating: 4.8,
    review_count: 128,
    is_available: true,
    teaching_regions: ['龙亭区', '金明区'],
    gender: 'male',
    bio: '两年家教经验，曾辅导多名初中生数学和物理，学生成绩提升显著。教学风格耐心细致，善于用生活中的例子讲解抽象概念。',
  },
  {
    teacher_id: 2,
    nickname: '李晓芳',
    avatar_url: '',
    avatar_bg: 'linear-gradient(135deg, #4ECDC4, #44BD32)',
    initial: '李',
    university: '河南大学',
    major: '外国语学院',
    grade: '研一',
    subjects: ['高中英语', '初中英语', '雅思'],
    min_price: 100,
    avg_rating: 4.9,
    review_count: 86,
    is_available: true,
    teaching_regions: ['龙亭区', '鼓楼区'],
    gender: 'female',
    bio: '英语专业八级，雅思7.5分。曾在新东方担任助教，有丰富的英语教学经验。擅长帮助学生提升英语阅读和写作能力。',
  },
  {
    teacher_id: 3,
    nickname: '王志强',
    avatar_url: '',
    avatar_bg: 'linear-gradient(135deg, #A29BFE, #6C5CE7)',
    initial: '王',
    university: '河南大学',
    major: '物理与电子学院',
    grade: '大四',
    subjects: ['高中物理', '竞赛辅导'],
    min_price: 120,
    avg_rating: 4.6,
    review_count: 52,
    is_available: true,
    teaching_regions: ['金明区', '顺河区'],
    gender: 'male',
    bio: '高考物理满分，大学物理竞赛省一等奖。擅长高中物理和竞赛辅导，曾辅导学生获得省级物理竞赛二等奖。',
  },
  {
    teacher_id: 4,
    nickname: '陈思雨',
    avatar_url: '',
    avatar_bg: 'linear-gradient(135deg, #FDCB6E, #F39C12)',
    initial: '陈',
    university: '河南大学',
    major: '化学化工学院',
    grade: '大三',
    subjects: ['初中化学', '高中化学'],
    min_price: 90,
    avg_rating: 4.7,
    review_count: 35,
    is_available: true,
    teaching_regions: ['龙亭区'],
    gender: 'female',
    bio: '化学专业，拥有高中化学教师资格证。注重实验思维培养，帮助学生从原理上理解化学反应。',
  },
  {
    teacher_id: 5,
    nickname: '刘浩然',
    avatar_url: '',
    avatar_bg: 'linear-gradient(135deg, #55E7FC, #0093E9)',
    initial: '刘',
    university: '河南大学',
    major: '文学院',
    grade: '大二',
    subjects: ['小学语文', '初中语文', '高中语文'],
    min_price: 70,
    avg_rating: 4.5,
    review_count: 18,
    is_available: true,
    teaching_regions: ['龙亭区', '金明区', '鼓楼区'],
    gender: 'male',
    bio: '语文教育专业，擅长作文辅导和阅读理解。曾获得全国大学生作文比赛二等奖。',
  },
]

// ============================================================
// 教师详情（含完整信息）
// ============================================================
export const mockTeacherDetail = {
  teacher_id: 1,
  nickname: '张明远',
  avatar_url: '',
  avatar_bg: 'linear-gradient(135deg, #FF6B6B, #EE5A24)',
  initial: '张',
  real_name: '张明远',
  gender: 'male',
  university: '河南大学',
  major: '数学与统计学院',
  grade: '大三',
  bio: '两年家教经验，曾辅导多名初中生数学和物理，学生成绩提升显著。教学风格耐心细致，善于用生活中的例子讲解抽象概念。\n\n教学理念：因材施教，注重培养学生的数学思维和解题能力，而非单纯刷题。',
  min_price: 80,
  avg_rating: 4.8,
  review_count: 128,
  is_available: true,
  teaching_regions: ['龙亭区', '金明区'],
  certificates: [
    { cert_type: 'student_card', image_url: '', label: '学生证' },
    { cert_type: 'cet4', image_url: '', label: '英语四级证书' },
    { cert_type: 'award', image_url: '', label: '数学竞赛获奖证书' },
  ],
  subjects: [
    { subject: '初中数学', grade_level: 'junior_1', unit_price: 80 },
    { subject: '初中物理', grade_level: 'junior_2', unit_price: 80 },
    { subject: '高中数学', grade_level: 'senior_1', unit_price: 100 },
  ],
  schedules: [
    { day_of_week: 1, day_name: '周一', start_time: '18:00', end_time: '20:00', status: 'available' },
    { day_of_week: 3, day_name: '周三', start_time: '19:00', end_time: '21:00', status: 'available' },
    { day_of_week: 6, day_name: '周六', start_time: '09:00', end_time: '17:00', status: 'available' },
    { day_of_week: 7, day_name: '周日', start_time: '14:00', end_time: '18:00', status: 'available' },
  ],
  reviews: [
    {
      parent_nickname: '家***长',
      teaching_ability: 5,
      communication: 5,
      punctuality: 4,
      content: '张老师非常有耐心，我家孩子数学基础比较差，经过一个月的辅导，期中考试提高了20多分！',
      created_at: '2026-05-20 10:30:00',
    },
    {
      parent_nickname: '用***户',
      teaching_ability: 5,
      communication: 4,
      punctuality: 5,
      content: '讲题思路清晰，孩子很喜欢上张老师的课。会针对薄弱环节制定专门的学习计划。',
      created_at: '2026-05-15 14:20:00',
    },
    {
      parent_nickname: '微***信',
      teaching_ability: 4,
      communication: 5,
      punctuality: 5,
      content: '老师很负责任，每次上课都会提前准备教案，课后还会给家长反馈学习情况。',
      created_at: '2026-05-10 09:00:00',
    },
  ],
  contact_viewed: false,
  contact_expire_at: null,
  is_favorited: false,
}

// ============================================================
// 订单列表
// ============================================================
export const mockOrders = [
  {
    order_id: 1,
    order_no: 'HD202605220001',
    status: 'pending_confirm',
    status_label: '待确认',
    status_color: '#FF976A',
    teacher_name: '张明远',
    teacher_avatar_bg: 'linear-gradient(135deg, #FF6B6B, #EE5A24)',
    teacher_initial: '张',
    subject: '初中数学',
    grade: '初一',
    lesson_date: '2026-05-30',
    start_time: '09:00',
    end_time: '11:00',
    duration: 2.0,
    unit_price: 80,
    total_amount: 160.00,
    commission_rate: 0.15,
    commission_amount: 24.00,
    settlement_amount: 136.00,
    address: '龙亭区XX小区3号楼',
    paid_at: '2026-05-22 15:30:00',
    accepted_at: null,
    started_at: null,
    completed_at: null,
    confirmed_at: null,
    timeline: [
      { time: '2026-05-22 15:30', event: '订单支付成功', status: 'done' },
      { time: '待定', event: '教师确认接单', status: 'pending' },
      { time: '待定', event: '开始上课', status: 'pending' },
      { time: '待定', event: '确认完成', status: 'pending' },
    ],
    parent_name: '小明家长',
    parent_phone: '138****5678',
  },
  {
    order_id: 2,
    order_no: 'HD202605200002',
    status: 'pending_trial',
    status_label: '待试课',
    status_color: '#1989FA',
    teacher_name: '李晓芳',
    teacher_avatar_bg: 'linear-gradient(135deg, #4ECDC4, #44BD32)',
    teacher_initial: '李',
    subject: '高中英语',
    grade: '高二',
    lesson_date: '2026-05-25',
    start_time: '14:00',
    end_time: '16:00',
    duration: 2.0,
    unit_price: 100,
    total_amount: 200.00,
    commission_rate: 0.15,
    commission_amount: 30.00,
    settlement_amount: 170.00,
    address: '鼓楼区XX路XX号',
    paid_at: '2026-05-20 10:00:00',
    accepted_at: '2026-05-20 11:00:00',
    timeline: [
      { time: '2026-05-20 10:00', event: '订单支付成功', status: 'done' },
      { time: '2026-05-20 11:00', event: '教师确认接单', status: 'done' },
      { time: '2026-05-25 14:00', event: '开始上课', status: 'pending' },
      { time: '待定', event: '确认完成', status: 'pending' },
    ],
    parent_name: '小红家长',
    parent_phone: '136****4321',
  },
  {
    order_id: 3,
    order_no: 'HD202605150003',
    status: 'completed',
    status_label: '已完成',
    status_color: '#07C160',
    teacher_name: '王志强',
    teacher_avatar_bg: 'linear-gradient(135deg, #A29BFE, #6C5CE7)',
    teacher_initial: '王',
    subject: '高中物理',
    grade: '高三',
    lesson_date: '2026-05-16',
    start_time: '09:00',
    end_time: '11:00',
    duration: 2.0,
    unit_price: 120,
    total_amount: 240.00,
    commission_rate: 0.15,
    commission_amount: 36.00,
    settlement_amount: 204.00,
    address: '金明区XX小区',
    paid_at: '2026-05-15 09:00:00',
    accepted_at: '2026-05-15 09:30:00',
    started_at: '2026-05-16 09:00:00',
    completed_at: '2026-05-16 11:00:00',
    confirmed_at: '2026-05-16 20:00:00',
    timeline: [
      { time: '2026-05-15 09:00', event: '订单支付成功', status: 'done' },
      { time: '2026-05-15 09:30', event: '教师确认接单', status: 'done' },
      { time: '2026-05-16 09:00', event: '开始上课', status: 'done' },
      { time: '2026-05-16 11:00', event: '标记完成', status: 'done' },
      { time: '2026-05-16 20:00', event: '家长确认完成', status: 'done' },
    ],
    parent_name: '小刚家长',
    parent_phone: '137****9876',
  },
  {
    order_id: 4,
    order_no: 'HD202605100004',
    status: 'cancelled',
    status_label: '已取消',
    status_color: '#EE0A24',
    teacher_name: '陈思雨',
    teacher_avatar_bg: 'linear-gradient(135deg, #FDCB6E, #F39C12)',
    teacher_initial: '陈',
    subject: '初中化学',
    grade: '初三',
    lesson_date: '2026-05-12',
    start_time: '16:00',
    end_time: '18:00',
    duration: 2.0,
    unit_price: 90,
    total_amount: 180.00,
    commission_rate: 0.15,
    commission_amount: 0,
    settlement_amount: 0,
    address: '龙亭区XX中学附近',
    cancel_reason: '教师时间冲突，无法接单',
    timeline: [
      { time: '2026-05-10 11:00', event: '订单支付成功', status: 'done' },
      { time: '2026-05-10 12:00', event: '教师拒绝接单', status: 'done' },
      { time: '2026-05-10 12:00', event: '已退款', status: 'done' },
    ],
    parent_name: '小花家长',
    parent_phone: '135****7890',
  },
]

// ============================================================
// 虚拟币钱包
// ============================================================
export const mockWallet = {
  balance: 35,
  total_recharged: 50,
  total_spent: 15,
}

export const mockWalletTransactions = [
  {
    transaction_id: 1,
    type: 'consume',
    amount: -5,
    balance_after: 35,
    description: '查看张明远老师联系方式',
    created_at: '2026-05-22 15:00:00',
  },
  {
    transaction_id: 2,
    type: 'consume',
    amount: -5,
    balance_after: 40,
    description: '查看李晓芳老师联系方式',
    created_at: '2026-05-20 10:30:00',
  },
  {
    transaction_id: 3,
    type: 'consume',
    amount: -5,
    balance_after: 45,
    description: '查看王志强老师联系方式',
    created_at: '2026-05-18 14:00:00',
  },
  {
    transaction_id: 4,
    type: 'recharge',
    amount: 50,
    balance_after: 50,
    description: '微信充值',
    created_at: '2026-05-15 09:00:00',
  },
]

// ============================================================
// 充值套餐
// ============================================================
export const mockRechargePackages = [
  { id: 1, amount: 10, coins: 10, label: '¥10 = 10币', popular: false },
  { id: 2, amount: 30, coins: 30, label: '¥30 = 30币', popular: false },
  { id: 3, amount: 50, coins: 50, label: '¥50 = 50币', popular: true },
  { id: 4, amount: 100, coins: 100, label: '¥100 = 100币', popular: false },
]

// ============================================================
// 教师端订单
// ============================================================
export const mockTeacherOrders = [
  {
    order_id: 1,
    order_no: 'HD202605220001',
    status: 'pending_confirm',
    status_label: '待确认',
    status_color: '#FF976A',
    parent_name: '小**长',
    parent_phone: '138****5678',
    subject: '初中数学',
    grade: '初一',
    lesson_date: '2026-05-30',
    start_time: '09:00',
    end_time: '11:00',
    duration: 2.0,
    unit_price: 80,
    total_amount: 160.00,
    commission_rate: 0.15,
    settlement_amount: 136.00,
    address: '龙亭区XX小区3号楼',
    paid_at: '2026-05-22 15:30:00',
    accepted_at: null,
    parent_note: '孩子数学基础一般，希望从基础知识开始辅导',
  },
  {
    order_id: 2,
    order_no: 'HD202605200002',
    status: 'pending_trial',
    status_label: '待试课',
    status_color: '#1989FA',
    parent_name: '小**长',
    parent_phone: '136****4321',
    subject: '初中物理',
    grade: '初二',
    lesson_date: '2026-05-25',
    start_time: '14:00',
    end_time: '16:00',
    duration: 2.0,
    unit_price: 80,
    total_amount: 160.00,
    commission_rate: 0.15,
    settlement_amount: 136.00,
    address: '龙亭区XX路XX号',
    paid_at: '2026-05-20 10:00:00',
    accepted_at: '2026-05-20 11:00:00',
    parent_note: '',
  },
  {
    order_id: 3,
    order_no: 'HD202605150003',
    status: 'in_progress',
    status_label: '进行中',
    status_color: '#1989FA',
    parent_name: '小**长',
    parent_phone: '137****9876',
    subject: '高中数学',
    grade: '高二',
    lesson_date: '2026-05-23',
    start_time: '09:00',
    end_time: '11:00',
    duration: 2.0,
    unit_price: 100,
    total_amount: 200.00,
    commission_rate: 0.15,
    settlement_amount: 170.00,
    address: '金明区XX小区',
    paid_at: '2026-05-15 09:00:00',
    accepted_at: '2026-05-15 09:30:00',
    started_at: '2026-05-23 09:00:00',
    parent_note: '希望重点辅导函数和解析几何',
  },
  {
    order_id: 4,
    order_no: 'HD202605100004',
    status: 'completed',
    status_label: '已完成',
    status_color: '#07C160',
    parent_name: '小**长',
    parent_phone: '135****7890',
    subject: '初中数学',
    grade: '初三',
    lesson_date: '2026-05-10',
    start_time: '16:00',
    end_time: '18:00',
    duration: 2.0,
    unit_price: 80,
    total_amount: 160.00,
    commission_rate: 0.15,
    commission_amount: 24.00,
    settlement_amount: 136.00,
    address: '金明区XX中学附近',
    paid_at: '2026-05-08 14:00:00',
    accepted_at: '2026-05-08 15:00:00',
    started_at: '2026-05-10 16:00:00',
    completed_at: '2026-05-10 18:00:00',
    confirmed_at: '2026-05-11 10:00:00',
    parent_note: '',
  },
]

// ============================================================
// 教师收入
// ============================================================
export const mockTeacherIncome = {
  withdrawable_balance: 680.00,
  total_income: 2360.00,
  pending_income: 340.00,
}

export const mockTeacherIncomeRecords = [
  {
    record_id: 1,
    order_no: 'HD202605160005',
    subject: '初中数学',
    grade: '初二',
    lesson_date: '2026-05-16',
    total_amount: 160.00,
    commission_amount: 24.00,
    settlement_amount: 136.00,
    status: '已结算',
    created_at: '2026-05-17 10:00:00',
  },
  {
    record_id: 2,
    order_no: 'HD202605120006',
    subject: '高中数学',
    grade: '高一',
    lesson_date: '2026-05-12',
    total_amount: 200.00,
    commission_amount: 30.00,
    settlement_amount: 170.00,
    status: '已结算',
    created_at: '2026-05-13 10:00:00',
  },
  {
    record_id: 3,
    order_no: 'HD202605080007',
    subject: '初中物理',
    grade: '初三',
    lesson_date: '2026-05-08',
    total_amount: 160.00,
    commission_amount: 24.00,
    settlement_amount: 136.00,
    status: '已结算',
    created_at: '2026-05-09 10:00:00',
  },
  {
    record_id: 4,
    order_no: 'HD202605050008',
    subject: '初中数学',
    grade: '初一',
    lesson_date: '2026-05-05',
    total_amount: 240.00,
    commission_amount: 36.00,
    settlement_amount: 204.00,
    status: '已结算',
    created_at: '2026-05-06 10:00:00',
  },
]

// ============================================================
// 教师审核状态
// ============================================================
export const mockTeacherAuditStatus = {
  // 'pending' | 'approved' | 'rejected'
  status: 'pending',
  status_label: '审核中',
  status_color: '#FF976A',
  status_bg: '#FFF7EE',
  submitted_at: '2026-05-22 16:00:00',
  audited_at: null,
  reject_reason: '',
  // 已填写的信息（审核中时展示）
  profile: {
    real_name: '张明远',
    gender: 'male',
    university: '河南大学',
    major: '数学与统计学院',
    grade: '大三',
    bio: '两年家教经验，曾辅导多名初中生数学和物理...',
    min_price: 80,
    teaching_regions: ['龙亭区', '金明区'],
    subjects: ['初中数学', '初中物理', '高中数学'],
    certificates_count: 3,
  },
}

// ============================================================
// 筛选选项
// ============================================================
export const mockFilterOptions = {
  subjects: ['数学', '英语', '物理', '化学', '语文', '生物', '历史', '地理', '政治'],
  grades: ['小学','初中','高中','一年级','二年级','三年级','四年级','五年级','六年级','初一','初二','初三','高一','高二','高三'],
  priceRanges: [
    { label: '全部价格', min: 0, max: 999 },
    { label: '¥50以下', min: 0, max: 50 },
    { label: '¥50-80', min: 50, max: 80 },
    { label: '¥80-120', min: 80, max: 120 },
    { label: '¥120以上', min: 120, max: 999 },
  ],
  regions: ['龙亭区', '顺河区', '鼓楼区', '禹王台区', '金明区'],
}

// ============================================================
// 科目映射
// ============================================================
export const subjectMap = {
  'math': '数学',
  'english': '英语',
  'physics': '物理',
  'chemistry': '化学',
  'chinese': '语文',
  'biology': '生物',
  'history': '历史',
  'geography': '地理',
  'politics': '政治',
}

// ============================================================
// 教师入驻表单用选项
// ============================================================
export const applyOptions = {
  genders: [
    { label: '男', value: 'male' },
    { label: '女', value: 'female' },
  ],
  grades: [
    { label: '大一', value: 'freshman' },
    { label: '大二', value: 'sophomore' },
    { label: '大三', value: 'junior' },
    { label: '大四', value: 'senior' },
    { label: '研一', value: 'master_1' },
    { label: '研二', value: 'master_2' },
    { label: '研三', value: 'master_3' },
  ],
  allSubjects: [
    { label: '小学语文', value: 'primary_chinese' },
    { label: '小学数学', value: 'primary_math' },
    { label: '小学英语', value: 'primary_english' },
    { label: '初中语文', value: 'junior_chinese' },
    { label: '初中数学', value: 'junior_math' },
    { label: '初中英语', value: 'junior_english' },
    { label: '初中物理', value: 'junior_physics' },
    { label: '初中化学', value: 'junior_chemistry' },
    { label: '初中生物', value: 'junior_biology' },
    { label: '高中语文', value: 'senior_chinese' },
    { label: '高中数学', value: 'senior_math' },
    { label: '高中英语', value: 'senior_english' },
    { label: '高中物理', value: 'senior_physics' },
    { label: '高中化学', value: 'senior_chemistry' },
    { label: '高中生物', value: 'senior_biology' },
    { label: '高中历史', value: 'senior_history' },
    { label: '高中地理', value: 'senior_geography' },
    { label: '高中政治', value: 'senior_politics' },
    { label: '竞赛辅导', value: 'competition' },
    { label: '雅思/托福', value: 'ielts_toefl' },
    { label: '其他', value: 'other' },
  ],
  teachingGrades: [
    { label: '小学一年级', value: 'primary_1' },
    { label: '小学二年级', value: 'primary_2' },
    { label: '小学三年级', value: 'primary_3' },
    { label: '小学四年级', value: 'primary_4' },
    { label: '小学五年级', value: 'primary_5' },
    { label: '小学六年级', value: 'primary_6' },
    { label: '初中一年级', value: 'junior_1' },
    { label: '初中二年级', value: 'junior_2' },
    { label: '初中三年级', value: 'junior_3' },
    { label: '高中一年级', value: 'senior_1' },
    { label: '高中二年级', value: 'senior_2' },
    { label: '高中三年级', value: 'senior_3' },
  ],
  regions: [
    { label: '龙亭区', value: '龙亭区' },
    { label: '顺河区', value: '顺河区' },
    { label: '鼓楼区', value: '鼓楼区' },
    { label: '禹王台区', value: '禹王台区' },
    { label: '金明区', value: '金明区' },
  ],
}

// ============================================================
// 订单状态映射
// ============================================================
export const orderStatusMap = {
  pending_confirm: { label: '待确认', color: '#FF976A', bg: '#FFF7EE' },
  pending_trial: { label: '待试课', color: '#1989FA', bg: '#EEF4FF' },
  in_progress: { label: '进行中', color: '#1989FA', bg: '#EEF4FF' },
  pending_settlement: { label: '待结算', color: '#FF976A', bg: '#FFF7EE' },
  completed: { label: '已完成', color: '#07C160', bg: '#E8F8EF' },
  cancelled: { label: '已取消', color: '#EE0A24', bg: '#FFF0F0' },
  dispute: { label: '纠纷中', color: '#EE0A24', bg: '#FFF0F0' },
}

// ============================================================
// 订单Tab配置
// ============================================================
// 家长端订单tab
export const parentOrderTabs = [
  { name: '全部', value: 'all' },
  { name: '待确认', value: 'pending_confirm' },
  { name: '进行中', value: 'active' }, // 待试课+进行中+待结算
  { name: '待结算', value: 'pending_settlement' },
  { name: '已完成', value: 'completed' },
  { name: '已取消', value: 'cancelled' },
]

// 教师端订单tab
export const teacherOrderTabs = [
  { name: '全部', value: 'all' },
  { name: '待确认', value: 'pending_confirm' },
  { name: '待试课', value: 'pending_trial' },
  { name: '进行中', value: 'in_progress' },
  { name: '已完成', value: 'completed' },
  { name: '已取消', value: 'cancelled' },
]
