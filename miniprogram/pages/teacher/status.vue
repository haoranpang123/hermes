<template>
  <!-- 教师审核状态页 -->
  <view class="status-page">
    <!-- 状态展示 -->
    <view class="status-card" :style="{ background: statusInfo.bg }">
      <view class="status-icon">{{ statusInfo.icon }}</view>
      <text class="status-title">入驻审核</text>
      <text class="status-label" :style="{ color: statusInfo.color }">
        {{ statusInfo.label }}
      </text>
      <text class="status-time">提交时间：{{ statusData.submitted_at }}</text>
    </view>

    <!-- 已通过状态 -->
    <view v-if="statusData.status === 'approved'" class="success-section">
      <view class="section">
        <text class="section-title">🎉 审核已通过</text>
        <text class="section-desc">您现在可以开始接单了！</text>
      </view>
      <view class="action-btn-wrapper">
        <u-button type="primary" shape="circle" size="large" @click="goToOrders">
          查看订单
        </u-button>
        <u-button type="primary" plain shape="circle" size="large" class="mt-12" @click="goToIncome">
          收入管理
        </u-button>
      </view>
    </view>

    <!-- 已驳回状态 -->
    <view v-if="statusData.status === 'rejected'" class="reject-section">
      <view class="section">
        <text class="section-title">❌ 审核未通过</text>
        <view class="reject-reason">
          <text class="reason-label">驳回原因：</text>
          <text class="reason-text">{{ statusData.reject_reason || '无' }}</text>
        </view>
      </view>
      <view class="action-btn-wrapper">
        <u-button type="primary" shape="circle" size="large" @click="reApply">
          修改资料重新提交
        </u-button>
      </view>
    </view>

    <!-- 待审核状态 - 查看已提交资料 -->
    <view v-if="statusData.status === 'pending'" class="pending-section">
      <view class="section">
        <text class="section-title">📋 已提交资料</text>
        <text class="section-desc">审核期间资料不可编辑</text>
      </view>

      <view class="info-card" v-if="statusData.profile">
        <view class="info-row">
          <text class="info-label">真实姓名</text>
          <text class="info-value">{{ statusData.profile.real_name }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">性别</text>
          <text class="info-value">{{ statusData.profile.gender === 'male' ? '男' : '女' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">学校</text>
          <text class="info-value">{{ statusData.profile.university }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">专业</text>
          <text class="info-value">{{ statusData.profile.major }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">年级</text>
          <text class="info-value">{{ statusData.profile.grade }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">教学科目</text>
          <text class="info-value">{{ statusData.profile.subjects.join('、') }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">课时费</text>
          <text class="info-value price">¥{{ statusData.profile.min_price }}/小时</text>
        </view>
        <view class="info-row">
          <text class="info-label">授课区域</text>
          <text class="info-value">{{ statusData.profile.teaching_regions.join('、') }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">证书数量</text>
          <text class="info-value">{{ statusData.profile.certificates_count }}张</text>
        </view>
        <view class="info-row">
          <text class="info-label">个人简介</text>
        </view>
        <text class="bio-text">{{ statusData.profile.bio }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { fetchData } from '@/utils/api.js'

export default {
  data() {
    return {
      statusData: {
        status: 'pending',
        submitted_at: '',
        reject_reason: '',
        profile: null,
      },
    }
  },

  computed: {
    statusInfo() {
      const map = {
        pending: {
          label: '审核中',
          color: '#FF976A',
          bg: '#FFF7EE',
          icon: '⏳',
        },
        approved: {
          label: '已通过',
          color: '#07C160',
          bg: '#E8F8EF',
          icon: '✅',
        },
        rejected: {
          label: '已驳回',
          color: '#EE0A24',
          bg: '#FFF0F0',
          icon: '❌',
        },
      }
      return map[this.statusData.status] || map.pending
    },
  },

  async onLoad() {
    try {
      const status = await fetchData('/api/v1/teacher/status')
      this.statusData.status = status.audit_status || 'pending'
      this.statusData.submitted_at = status.created_at || ''
      this.statusData.reject_reason = status.audit_reason || ''

      // 审核通过则加载完整资料
      if (this.statusData.status === 'approved') {
        try {
          const profile = await fetchData('/api/v1/teacher/profile')
          this.statusData.profile = profile
        } catch (e) {
          // profile load failed, not critical
        }
      }
    } catch (e) {
      // fallback: keep default pending
    }
  },

  methods: {
    /**
     * 重新提交申请
     */
    reApply() {
      uni.navigateTo({ url: '/pages/teacher/apply' })
    },

    /**
     * 查看订单
     */
    goToOrders() {
      uni.navigateTo({ url: '/pages/teacher/orders' })
    },

    /**
     * 收入管理
     */
    goToIncome() {
      uni.navigateTo({ url: '/pages/teacher/income' })
    },
  },
}
</script>

<style lang="scss" scoped>
.status-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding: 12px;
}

.status-card {
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  margin-bottom: 12px;

  .status-icon {
    font-size: 48px;
    margin-bottom: 8px;
  }

  .status-title {
    font-size: 16px;
    color: #666666;
    display: block;
  }

  .status-label {
    font-size: 24px;
    font-weight: 700;
    display: block;
    margin: 8px 0;
  }

  .status-time {
    font-size: 12px;
    color: #999999;
    display: block;
  }
}

.section {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1A1A1A;
    display: block;
    margin-bottom: 4px;
  }

  .section-desc {
    font-size: 13px;
    color: #999999;
  }
}

.reject-reason {
  margin-top: 8px;
  padding: 10px;
  background: #FFF0F0;
  border-radius: 8px;

  .reason-label {
    font-size: 13px;
    color: #EE0A24;
    font-weight: 600;
  }

  .reason-text {
    font-size: 13px;
    color: #666666;
    margin-left: 4px;
  }
}

.info-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    font-size: 14px;

    .info-label {
      color: #666666;
    }

    .info-value {
      color: #1A1A1A;

      &.price {
        color: #EE0A24;
        font-weight: 600;
      }
    }
  }

  .bio-text {
    font-size: 14px;
    color: #666666;
    line-height: 1.6;
    margin-top: 4px;
    display: block;
  }
}

.action-btn-wrapper {
  padding: 16px 0;

  .mt-12 {
    margin-top: 12px;
  }
}
</style>
