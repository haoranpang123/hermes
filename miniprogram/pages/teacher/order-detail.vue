<template>
  <!-- 教师订单详情页 -->
  <view class="detail-page">
    <!-- 订单状态 -->
    <view class="status-bar" :style="{ background: getStatusInfo(order.status).bg }">
      <text class="status-text" :style="{ color: getStatusInfo(order.status).color }">
        {{ getStatusInfo(order.status).label }}
      </text>
    </view>

    <!-- 订单信息 -->
    <view class="info-card">
      <view class="card-title">订单信息</view>
      <view class="info-row">
        <text class="info-label">订单编号</text>
        <text class="info-value">{{ order.order_no }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">家长</text>
        <text class="info-value">{{ order.parent_name }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">联系电话</text>
        <text class="info-value">{{ order.parent_phone }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">科目</text>
        <text class="info-value">{{ order.subject }} · {{ order.grade }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">日期</text>
        <text class="info-value">{{ order.lesson_date }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">时间</text>
        <text class="info-value">{{ order.start_time }} - {{ order.end_time }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">课时</text>
        <text class="info-value">{{ order.duration }}小时</text>
      </view>
      <view class="info-row">
        <text class="info-label">地址</text>
        <text class="info-value">{{ order.address }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">家长备注</text>
        <text class="info-value">{{ order.parent_note || '无' }}</text>
      </view>
    </view>

    <!-- 金额信息 -->
    <view class="info-card">
      <view class="card-title">金额信息</view>
      <view class="info-row">
        <text class="info-label">单价</text>
        <text class="info-value">¥{{ order.unit_price }}/小时</text>
      </view>
      <view class="info-row">
        <text class="info-label">订单总额</text>
        <text class="info-value">¥{{ order.total_amount.toFixed(2) }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">平台佣金</text>
        <text class="info-value">
          ¥{{ (order.commission_amount || order.total_amount * 0.15).toFixed(2) }}
        </text>
      </view>
      <view class="divider" />
      <view class="info-row total-row">
        <text class="info-label">预计收入</text>
        <text class="info-value amount">¥{{ order.settlement_amount.toFixed(2) }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-area" v-if="showActions">
      <template v-if="order.status === 'pending_confirm'">
        <u-button type="primary" shape="circle" size="large" @click="handleAccept">
          ✅ 确认接单
        </u-button>
        <u-button type="error" plain shape="circle" size="large" class="mt-12" @click="handleReject">
          ❌ 拒绝接单
        </u-button>
      </template>

      <template v-if="order.status === 'pending_trial'">
        <u-button type="primary" shape="circle" size="large" @click="handleStart">
          📝 标记上课
        </u-button>
      </template>

      <template v-if="order.status === 'in_progress'">
        <u-button type="primary" shape="circle" size="large" @click="handleComplete">
          ✅ 标记完成
        </u-button>
      </template>

      <view v-if="order.status === 'completed'" class="status-hint success">
        ✅ 订单已完成，收入已结算
      </view>

      <view v-if="order.status === 'cancelled'" class="status-hint danger">
        ❌ 订单已取消
      </view>
    </view>
  </view>
</template>

<script>
import { orderStatusMap } from '@/common/mock.js'
import { fetchData, postData } from '@/utils/api.js'

export default {
  data() {
    return {
      order: {},
      loading: true,
    }
  },

  computed: {
    showActions() {
      return ['pending_confirm', 'pending_trial', 'in_progress'].includes(this.order.status)
    },
  },

  async onLoad(options) {
    if (options.id) {
      try {
        this.loading = true
        const data = await fetchData(`/api/v1/orders/${options.id}`)
        this.order = data
      } catch (e) {
        // error handled by api util
      } finally {
        this.loading = false
      }
    }
  },

  methods: {
    getStatusInfo(status) {
      return orderStatusMap[status] || { label: status, color: '#999999', bg: '#F5F5F5' }
    },

    async handleAccept() {
      uni.showModal({
        title: '确认接单',
        content: '确认接受此订单？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${this.order.order_id}/accept`)
              uni.showToast({ title: '已接单', icon: 'success' })
              this.refreshOrder()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    async handleReject() {
      uni.showModal({
        title: '拒绝接单',
        content: '确认拒绝此订单？订单将退款给家长。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${this.order.order_id}/reject`, {
                reason: '教师拒绝接单',
              })
              uni.showToast({ title: '已拒绝', icon: 'none' })
              this.refreshOrder()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    async handleStart() {
      uni.showModal({
        title: '标记上课',
        content: '确认开始上课？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${this.order.order_id}/start`)
              uni.showToast({ title: '已标记', icon: 'success' })
              this.refreshOrder()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    async handleComplete() {
      uni.showModal({
        title: '标记完成',
        content: '确认课程已完成？标记后等待家长确认。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${this.order.order_id}/complete`)
              uni.showToast({ title: '已完成', icon: 'success' })
              this.refreshOrder()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    /**
     * 刷新订单详情
     */
    async refreshOrder() {
      try {
        const data = await fetchData(`/api/v1/orders/${this.order.order_id}`)
        this.order = data
      } catch (e) {
        // error handled by api util
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.detail-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding: 12px;
}

.status-bar {
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  margin-bottom: 12px;

  .status-text {
    font-size: 18px;
    font-weight: 700;
  }
}

.info-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: #1A1A1A;
    margin-bottom: 12px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    font-size: 14px;

    .info-label {
      color: #666666;
    }

    .info-value {
      color: #1A1A1A;
      text-align: right;
      max-width: 60%;
    }

    &.total-row {
      .amount {
        font-size: 18px;
        font-weight: 700;
        color: #07C160;
      }
    }
  }

  .divider {
    height: 1px;
    background: #EBEDF0;
    margin: 6px 0;
  }
}

.action-area {
  margin-top: 16px;

  .mt-12 {
    margin-top: 12px;
  }

  .status-hint {
    text-align: center;
    font-size: 14px;
    padding: 16px;

    &.success {
      color: #07C160;
    }

    &.danger {
      color: #EE0A24;
    }
  }
}
</style>
