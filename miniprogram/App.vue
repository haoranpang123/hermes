<script>
/**
 * 河大家教小程序 — App.vue
 * 全局应用入口
 */
export default {
  globalData: {
    // 用户信息
    userInfo: null,
    token: '',
    // 用户角色：null（未选择）/ 'parent'（家长）/ 'teacher'（教师）
    role: null,
    // 教师审核状态（教师端用）
    teacherAuditStatus: null
  },
  onLaunch() {
    console.log('[App] 河大家教小程序启动')
    // 检查本地存储是否有登录状态
    const token = uni.getStorageSync('token')
    const userInfo = uni.getStorageSync('userInfo')
    const role = uni.getStorageSync('role')
    if (token) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      this.globalData.role = role
    }
  },
  onShow() {
    console.log('[App] onShow')
  },
  onHide() {
    console.log('[App] onHide')
  }
}
</script>

<style lang="scss">
/* 全局样式 */
@import 'uview-ui/index.scss';

/* 使用 Design Token 的全局辅助类 */
page {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  color: #1A1A1A;
  background-color: #F5F5F5;
}

/* 卡片通用样式 */
.app-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 页面通用 padding */
.app-page-content {
  padding: 12px;
}

/* 金额样式 */
.app-amount {
  color: #EE0A24;
  font-weight: 600;
}

.app-amount-green {
  color: #07C160;
  font-weight: 600;
}

/* 文字辅助类 */
.app-text-hint {
  color: #999999;
  font-size: 12px;
}

.app-text-secondary {
  color: #666666;
}

/* 分割线 */
.app-divider {
  height: 1px;
  background: #EBEDF0;
  margin: 10px 0;
}

/* 弹性布局 */
.app-flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-flex-center {
  display: flex;
  align-items: center;
}

/* 安全区域底部 */
.app-safe-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0);
}

/* 卡片底部操作栏 */
.app-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #F0F0F0;
}
</style>
