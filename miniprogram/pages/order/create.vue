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
          <text class="info-value">{{ orderInfo.lesson_date }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">上课时间</text>
          <text class="info-value">{{ orderInfo.start_time }} - {{ orderInfo.end_time }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">上课地址</text>
          <text class="info-value">{{ orderInfo.address }}</text>
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
      title="支付成功"
      content="首课费用已托管至平台，教师接单后将自动安排上课。"
      show-cancel-button
      confirm-text="查看订单"
      cancel-text="返回首页"
      @confirm="goToOrders"
      @cancel="goHome"
    />
  </view>
</template>

<script>
import { mockTeachers } from '@/common/mock.js'

export default {
  data() {
    return {
      orderInfo: {
        teacher_id: null,
        teacher_name: '',
        subject: '',
        grade: '',
        lesson_date: '2026-05-30',
        start_time: '09:00',
        end_time: '11:00',
        duration: 2.0,
        unit_price: 80,
        total_amount: 160.0,
        address: '龙亭区XX小区3号楼',
      },
      paying: false,
      showSuccess: false,
    }
  },

  onLoad(options) {
    // 从教师详情页接收参数
    if (options.teacher_id) {
      const teacher = mockTeachers.find(t => t.teacher_id === parseInt(options.teacher_id))
      if (teacher) {
        this.orderInfo.teacher_id = teacher.teacher_id
        this.orderInfo.teacher_name = teacher.nickname
        this.orderInfo.subject = options.subject || teacher.subjects[0] || ''
        this.orderInfo.unit_price = parseInt(options.price) || teacher.min_price
        this.orderInfo.total_amount = this.orderInfo.unit_price * this.orderInfo.duration
      }
    }
  },

  methods: {
    /**
     * 微信支付
     * 模拟支付流程
     */
    handlePay() {
      this.paying = true
      // 模拟微信支付
      setTimeout(() => {
        this.paying = false
        this.showSuccess = true
      }, 1500)
    },

    /**
     * 跳转订单列表
     */
    goToOrders() {
      this.showSuccess = false
      uni.switchTab({ url: '/pages/order/list' })
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
      }

      .info-value {
        color: #1A1A1A;
        text-align: right;
        max-width: 60%;
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
