<template>
  <!-- 登录页面：微信一键登录 + 手机号绑定 + 身份选择 -->
  <view class="login-page">
    <view class="login-container">
      <!-- Logo & 标题 -->
      <view class="login-header">
        <view class="logo-wrapper">
          <view class="logo-icon">🎓</view>
        </view>
        <text class="app-name">河大家教</text>
        <text class="app-slogan">大学生家教，靠谱又实惠</text>
      </view>

      <!-- 步骤1：微信登录 -->
      <view class="login-step" v-if="step === 1">
        <view class="step-desc">授权微信登录，快速进入</view>
        <u-button
          type="primary"
          shape="circle"
          size="large"
          @click="handleWechatLogin"
          :loading="loading"
          class="login-btn wechat-btn"
        >
          <u-icon name="weixin-fill" size="20" color="#fff" style="margin-right: 8px" />
          <text>微信一键登录</text>
        </u-button>
        <view class="agreement-text">
          登录即表示同意《用户协议》和《隐私政策》
        </view>
      </view>

      <!-- 步骤2：手机号绑定 -->
      <view class="login-step" v-if="step === 2">
        <view class="step-desc">绑定手机号，保障账户安全</view>
        <u-button
          type="primary"
          shape="circle"
          size="large"
          open-type="getPhoneNumber"
          @getphonenumber="handleGetPhoneNumber"
          :loading="loading"
          class="login-btn"
        >
          <u-icon name="phone-fill" size="20" color="#fff" style="margin-right: 8px" />
          <text>微信手机号快速绑定</text>
        </u-button>
      </view>

      <!-- 步骤3：身份选择 -->
      <view class="login-step" v-if="step === 3">
        <view class="step-desc">请选择您的身份</view>
        <view class="role-options">
          <view class="role-card parent" @click="selectRole('parent')">
            <view class="role-icon">👨‍👩‍👧</view>
            <text class="role-title">我是家长</text>
            <text class="role-desc">找家教老师</text>
          </view>
          <view class="role-card teacher" @click="selectRole('teacher')">
            <view class="role-icon">👨‍🏫</view>
            <text class="role-title">我是教师</text>
            <text class="role-desc">入驻接家教</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { post, postData } from '@/utils/api.js'
import store, { saveLogin, updateUserInfo } from '@/store/index.js'

export default {
  data() {
    return {
      step: 1, // 1=微信登录, 2=手机绑定, 3=身份选择
      loading: false,
      phone: '',
    }
  },
  methods: {
    /**
     * 步骤1：微信一键登录
     * 调用 wx.login() 获取临时 code，POST /api/v1/auth/login 换取 JWT
     */
    async handleWechatLogin() {
      this.loading = true
      try {
        // 1. 调用微信登录获取 code
        const loginRes = await new Promise((resolve, reject) => {
          uni.login({
            success: resolve,
            fail: reject,
          })
        })

        if (!loginRes.code) {
          uni.showToast({ title: '获取微信授权失败', icon: 'none' })
          return
        }

        // 2. 调用后端登录接口
        const data = await postData('/api/v1/auth/login', { code: loginRes.code })

        const { token, user, is_new } = data

        // 3. 保存登录信息到 store
        saveLogin(token, user, user.role || '')

        // 4. 根据 is_new 决定下一步
        if (is_new) {
          // 新用户 → 进入手机号绑定
          this.step = 2
        } else if (user.role) {
          // 老用户已有角色 → 直接跳转
          this.navigateByRole(user.role)
        } else {
          // 老用户但无角色 → 进入身份选择
          this.step = 3
        }
      } catch (err) {
        uni.showToast({ title: err.message || '登录失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    /**
     * 步骤2：获取手机号并绑定
     * 微信 getPhoneNumber 回调 → POST /api/v1/auth/bind-phone
     */
    async handleGetPhoneNumber(e) {
      const phoneCode = e.detail && e.detail.code
      if (!phoneCode) {
        uni.showToast({ title: '获取手机号失败', icon: 'none' })
        return
      }

      this.loading = true
      try {
        // 调用后端绑定手机号
        const data = await postData('/api/v1/auth/bind-phone', { code: phoneCode })

        // 更新 store 中的用户信息（后端可能返回更新后的 user）
        if (data.user) {
          saveLogin(store.user.token, data.user, store.user.role)
        }

        this.phone = data.phone || '已绑定'
        // 进入身份选择步骤
        this.step = 3
      } catch (err) {
        uni.showToast({ title: err.message || '绑定手机号失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    /**
     * 步骤3：选择身份
     * 调用 POST /api/v1/auth/select-role 提交角色
     */
    async selectRole(role) {
      if (this.loading) return
      this.loading = true
      try {
        // 调用后端选择角色接口
        const data = await postData('/api/v1/auth/select-role', { role })

        // 用后端返回的最新信息更新 store
        if (data.user) {
          saveLogin(store.user.token, data.user, role)
        } else {
          // 手动更新 role
          updateUserInfo({ role })
        }

        this.navigateByRole(role)
      } catch (err) {
        uni.showToast({ title: err.message || '选择身份失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    /**
     * 根据角色跳转到对应页面
     */
    navigateByRole(role) {
      if (role === 'parent') {
        uni.switchTab({ url: '/pages/index/index' })
      } else {
        uni.redirectTo({ url: '/pages/teacher/apply' })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F8EF 0%, #FFFFFF 50%, #E8F8EF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.login-container {
  width: 100%;
  max-width: 320px;
}

.login-header {
  text-align: center;
  margin-bottom: 48px;

  .logo-wrapper {
    margin-bottom: 16px;

    .logo-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #07C160, #06AD56);
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40px;
      margin: 0 auto;
      box-shadow: 0 8px 24px rgba(7, 193, 96, 0.3);
    }
  }

  .app-name {
    font-size: 24px;
    font-weight: 700;
    color: #1A1A1A;
    display: block;
    margin-bottom: 8px;
  }

  .app-slogan {
    font-size: 14px;
    color: #666666;
  }
}

.login-step {
  text-align: center;

  .step-desc {
    font-size: 15px;
    color: #666666;
    margin-bottom: 24px;
  }
}

.login-btn {
  margin-bottom: 16px;
  height: 48px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 600;

  &.wechat-btn {
    background: #07C160;
    border-color: #07C160;
  }
}

.agreement-text {
  font-size: 12px;
  color: #999999;
  margin-top: 12px;
}

.role-options {
  display: flex;
  gap: 16px;
  justify-content: center;

  .role-card {
    flex: 1;
    background: #FFFFFF;
    border-radius: 12px;
    padding: 24px 16px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;

    &:active {
      transform: scale(0.97);
    }

    &.parent:active {
      border-color: #07C160;
      background: #E8F8EF;
    }

    &.teacher:active {
      border-color: #1989FA;
      background: #EEF4FF;
    }

    .role-icon {
      font-size: 40px;
      margin-bottom: 8px;
    }

    .role-title {
      font-size: 16px;
      font-weight: 600;
      color: #1A1A1A;
      display: block;
      margin-bottom: 4px;
    }

    .role-desc {
      font-size: 12px;
      color: #999999;
    }
  }
}
</style>
