<template>
  <!-- 下单支付页：确认信息 + 金额汇总 + 微信支付按钮 -->
  <view class="create-page">
    <!-- 订单确认卡片 -->
    <view class="order-card">
      <view class="card-title">订单确认</view>

      <view class="order-info">
        <view class="info-row">
          <text class="info-label">教师</text>
          <text class="info-value">{{ orderInfo.teacher_name }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">科目</text>
          <text class="info-value">{{ orderInfo.subject }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">上课日期</text>
          <picker mode="date" :value="orderInfo.lesson_date" @change="onDateChange">
            <text class="info-value picker-value" :class="{ placeholder: !orderInfo.lesson_date }">
              {{ orderInfo.lesson_date || '请选择日期' }}
            </text>
          </picker>
        </view>
        <view class="info-row">
          <text class="info-label">开始时间</text>
          <picker mode="time" :value="orderInfo.start_time" @change="onStartTimeChange">
            <text class="info-value picker-value" :class="{ placeholder: !orderInfo.start_time }">
              {{ orderInfo.start_time || '请选择开始时间' }}
            </text>
          </picker>
        </view>
        <view class="info-row">
          <text class="info-label">结束时间</text>
          <picker mode="time" :value="orderInfo.end_time" @change="onEndTimeChange">
            <text class="info-value picker-value" :class="{ placeholder: !orderInfo.end_time }">
              {{ orderInfo.end_time || '请选择结束时间' }}
            </text>
          </picker>
        </view>
        <view class="info-row">
          <text class="info-label">上课地址</text>
          <input
            class="info-input"
            v-model="orderInfo.address"
            placeholder="请输入上课地址"
            placeholder-style="color: #CCCCCC"
          />
        </view>
        <view class="info-row">
          <text class="info-label">备注</text>
          <input
            class="info-input"
            v-model="orderInfo.parent_note"
            placeholder="选填"
            placeholder-style="color: #CCCCCC"
          />
        </view>
        <view class="info-row">
          <text class="info-label">课时费</text>
          <text class="info-value">¥{{ orderInfo.unit_price }}/小时 × {{ orderInfo.duration }}小时</text>
        </view>
      </view>

      <view class="divider" />

      <view class="amount-row">
        <text class="amount-label">首课托管金额</text>
        <text class="amount-value">¥{{ orderInfo.total_amount }}</text>
      </view>

      <view class="escrow-hint">
        💡 课后满意才结算给教师，不满意可申请退款
      </view>
    </view>

    <!-- 微信支付按钮 -->
    <view class="pay-btn-wrapper">
      <u-button
        type="primary"
        shape="circle"
        size="large"
        @click="handlePay"
        :loading="paying"
        class="pay-btn"
      >
        <u-icon name="weixin-fill" size="18" color="#fff" style="margin-right: 6px" />
        <text>确认支付 ¥{{ orderInfo.total_amount }}</text>
      </u-button>
    </view>

    <!-- 支付成功弹窗 -->
    <u-modal
      v-model="showSuccess"
      title="下单成功"
      content="订单已创建，首课费用将托管至平台。教师接单后将自动安排上课。"
      show-cancel-button
      confirm-text="查看订单"
      cancel-text="返回首页"
      @confirm="goToOrders"
      @cancel="goHome"
    />
  </view>
</template>

<script>
import { postData } from '@/utils/api.js'

export default {
  data() {
    return {
      orderInfo: {
        teacher_id: null,
        teacher_name: '',
        subject: '',
        grade: '',
        lesson_date: '',
        start_time: '',
        end_time: '',
        duration: 2.0,
        unit_price: 80,
        total_amount: 160.0,
        address: '',
        parent_note: '',
      },
      paying: false,
      showSuccess: false,
      createdOrderId: null,
    }
  },

  computed: {
    /**
     * 动态计算时长（小时）
     */
    computedDuration() {
      if (!this.orderInfo.start_time || !this.orderInfo.end_time) return 0
      const [sh, sm] = this.orderInfo.start_time.split(':').map(Number)
      const [eh, em] = this.orderInfo.end_time.split(':').map(Number)
      const start = sh * 60 + sm
      const end = eh * 60 + em
      if (end <= start) return 0
      return Math.round(((end - start) / 60) * 10) / 10
    },
  },

  watch: {
    /**
     * 时长变化 → 重算总金额
     */
    computedDuration(val) {
      this.orderInfo.duration = val
      this.orderInfo.total_amount = Math.round(this.orderInfo.unit_price * val * 100) / 100
    },
    'orderInfo.unit_price'() {
      this.orderInfo.total_amount = Math.round(this.orderInfo.unit_price * this.orderInfo.duration * 100) / 100
    },
  },

  onLoad(options) {
    // 从教师详情页接收参数
    if (options.teacher_id) {
      this.orderInfo.teacher_id = parseInt(options.teacher_id) || options.teacher_id
      this.orderInfo.teacher_name = options.teacher_name || ''
      this.orderInfo.subject = options.subject || ''
      this.orderInfo.unit_price = parseInt(options.price) || 80
      this.orderInfo.total_amount = this.orderInfo.unit_price * this.orderInfo.duration
    }
  },

  methods: {
    /**
     * 日期选择
     */
    onDateChange(e) {
      this.orderInfo.lesson_date = e.detail.value
    },

    /**
     * 开始时间选择
     */
    onStartTimeChange(e) {
      this.orderInfo.start_time = e.detail.value
    },

    /**
     * 结束时间选择
     */
    onEndTimeChange(e) {
      this.orderInfo.end_time = e.detail.value
    },

    /**
     * 提交订单 → 调用 POST /api/v1/orders
     */
    async handlePay() {
      // 表单校验
      if (!this.orderInfo.lesson_date) {
        uni.showToast({ title: '请选择上课日期', icon: 'none' })
        return
      }
      if (!this.orderInfo.start_time) {
        uni.showToast({ title: '请选择开始时间', icon: 'none' })
        return
      }
      if (!this.orderInfo.end_time) {
        uni.showToast({ title: '请选择结束时间', icon: 'none' })
        return
      }
      if (!this.orderInfo.address.trim()) {
        uni.showToast({ title: '请输入上课地址', icon: 'none' })
        return
      }

      this.paying = true
      try {
        const body = {
          teacher_id: this.orderInfo.teacher_id,
          subject: this.orderInfo.subject,
          lesson_date: this.orderInfo.lesson_date,
          start_time: this.orderInfo.start_time,
          end_time: this.orderInfo.end_time,
          address: this.orderInfo.address.trim(),
          parent_note: this.orderInfo.parent_note ? this.orderInfo.parent_note.trim() : undefined,
        }
        const data = await postData('/api/v1/orders', body, { showLoading: true, loadingText: '提交中...' })
        this.createdOrderId = data.order_id
        this.showSuccess = true
      } catch (err) {
        uni.showToast({ title: err.message || '下单失败', icon: 'none' })
      } finally {
        this.paying = false
      }
    },

    /**
     * 跳转订单详情
     */
    goToOrders() {
      this.showSuccess = false
      if (this.createdOrderId) {
        uni.redirectTo({ url: `/pages/order/detail?id=${this.createdOrderId}` })
      } else {
        uni.switchTab({ url: '/pages/order/list' })
      }
    },

    /**
     * 返回首页
     */
    goHome() {
      this.showSuccess = false
      uni.switchTab({ url: '/pages/index/index' })
    },
  },
}
</script>

<style lang="scss" scoped>
.create-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding: 12px;
}

.order-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  .card-title {
    font-size: 16px;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 14px;
  }

  .order-info {
    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      font-size: 14px;

      .info-label {
        color: #666666;
        flex-shrink: 0;
      }

      .info-value {
        color: #1A1A1A;
        text-align: right;
        max-width: 60%;

        &.picker-value {
          color: #1A1A1A;
        }

        &.placeholder {
          color: #CCCCCC;
        }
      }

      .info-input {
        text-align: right;
        color: #1A1A1A;
        font-size: 14px;
        max-width: 60%;
        flex: 1;
      }
    }
  }

  .divider {
    height: 1px;
    background: #EBEDF0;
    margin: 12px 0;
  }

  .amount-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;

    .amount-label {
      font-size: 16px;
      font-weight: 600;
      color: #1A1A1A;
    }

    .amount-value {
      font-size: 20px;
      font-weight: 700;
      color: #EE0A24;
    }
  }

  .escrow-hint {
    margin-top: 8px;
    font-size: 12px;
    color: #FF976A;
    background: #FFF7EE;
    padding: 8px 12px;
    border-radius: 8px;
  }
}

.pay-btn-wrapper {
  margin-top: 32px;
  padding: 0 12px;

  .pay-btn {
    height: 48px;
    border-radius: 24px;
    font-size: 16px;
    font-weight: 600;
    background: #07C160;
    border-color: #07C160;
  }
}
</style>
