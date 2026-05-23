<template>
  <!-- 个人中心页 -->
  <view class="mine-page">
    <!-- 用户信息卡片 -->
    <view class="user-card" @click="editProfile">
      <view class="user-avatar">
        <view class="avatar-placeholder">👤</view>
      </view>
      <view class="user-info">
        <text class="user-name">{{ userInfo.nickname }}</text>
        <text class="user-tag">家长 · 已绑定手机号</text>
      </view>
      <u-icon name="arrow-right" size="16" color="#CCCCCC" />
    </view>

    <!-- 菜单列表 -->
    <u-cell-group>
      <u-cell
        title="我的订单"
        icon="order"
        :is-link="true"
        url="/pages/order/list"
      />
      <u-cell
        title="我的收藏"
        icon="heart"
        :is-link="true"
        @click="goToFavorites"
      />
      <u-cell
        title="我的钱包"
        icon="rmb-circle"
        :is-link="true"
        :value="'余额 ' + walletBalance + ' 币'"
        url="/pages/wallet/index"
      />
    </u-cell-group>

    <u-cell-group class="mt-12">
      <u-cell
        title="资料编辑"
        icon="edit-pen"
        :is-link="true"
        @click="editProfile"
      />
      <u-cell
        title="意见反馈"
        icon="chat"
        :is-link="true"
        @click="goFeedback"
      />
      <u-cell
        title="设置"
        icon="setting"
        :is-link="true"
        @click="goSettings"
      />
    </u-cell-group>

    <!-- 退出登录 -->
    <view class="logout-btn-wrapper">
      <u-button
        type="error"
        plain
        shape="circle"
        @click="handleLogout"
      >
        退出登录
      </u-button>
    </view>

    <!-- 版本信息 -->
    <view class="version-text">
      <text>河大家教 v1.0.0</text>
    </view>
  </view>
</template>

<script>
import store, { clearLogin } from '@/store/index.js'
import { fetchData } from '@/utils/api.js'

export default {
  data() {
    return {
      walletBalance: 0,
    }
  },

  computed: {
    userInfo() {
      return store.user.userInfo || { nickname: '未登录', avatar_url: '' }
    },
  },

  onShow() {
    // 每次显示时从后端获取最新钱包余额
    this.fetchWallet()
  },

  methods: {
    /**
     * 获取钱包余额
     */
    async fetchWallet() {
      try {
        const walletData = await fetchData('/api/v1/wallet')
        this.walletBalance = walletData.balance || 0
      } catch (e) {
        // 保持默认值
      }
    },
    /**
     * 编辑资料
     */
    editProfile() {
      uni.showToast({ title: '资料编辑（P1功能）', icon: 'none' })
    },

    /**
     * 我的收藏
     */
    goToFavorites() {
      uni.showToast({ title: '收藏列表（P1功能）', icon: 'none' })
    },

    /**
     * 意见反馈
     */
    goFeedback() {
      uni.showToast({ title: '意见反馈（P1功能）', icon: 'none' })
    },

    /**
     * 设置
     */
    goSettings() {
      uni.showToast({ title: '设置（P1功能）', icon: 'none' })
    },

    /**
     * 退出登录
     */
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '退出登录后需要重新授权',
        success: (res) => {
          if (res.confirm) {
            // 通过 store 清除登录状态
            clearLogin()
            uni.reLaunch({ url: '/pages/login/index' })
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.mine-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding-bottom: 20px;
}

.user-card {
  background: linear-gradient(135deg, #07C160, #06AD56);
  padding: 24px 16px;
  display: flex;
  align-items: center;
  gap: 14px;

  .user-avatar {
    .avatar-placeholder {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 30px;
      color: #FFFFFF;
    }
  }

  .user-info {
    flex: 1;

    .user-name {
      font-size: 18px;
      font-weight: 600;
      color: #FFFFFF;
      display: block;
    }

    .user-tag {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 4px;
      display: block;
    }
  }
}

.mt-12 {
  margin-top: 12px;
}

.logout-btn-wrapper {
  padding: 24px 16px;
}

.version-text {
  text-align: center;
  font-size: 12px;
  color: #999999;
  padding: 16px 0;
}
</style>
