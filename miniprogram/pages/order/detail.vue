<template>
  <!-- 订单详情页：状态时间线 + 订单信息 + 动态操作按钮 -->
  <view class="detail-page">
    <!-- 状态时间线 -->
    <view class="timeline-card">
      <view class="card-title">订单进度</view>
      <u-steps
        :list="timelineList"
        :current="timelineCurrent"
        direction="column"
        activeColor="#07C160"
        inactiveColor="#CCCCCC"
      />
    </view>

    <!-- 订单信息 -->
    <view class="info-card">
      <view class="card-title">订单信息</view>
      <view class="info-row">
        <text class="info-label">订单编号</text>
        <text class="info-value">{{ order.order_no }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">订单状态</text>
        <text class="info-value" :style="{ color: order.status_color }">
          {{ order.status_label }}
        </text>
      </view>
      <view class="info-row">
        <text class="info-label">教师</text>
        <text class="info-value">{{ order.teacher_name }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">科目</text>
        <text class="info-value">{{ order.subject }} · {{ order.grade }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">上课日期</text>
        <text class="info-value">{{ order.lesson_date }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">上课时间</text>
        <text class="info-value">{{ order.start_time }} - {{ order.end_time }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">课时</text>
        <text class="info-value">{{ order.duration }}小时</text>
      </view>
      <view class="info-row">
        <text class="info-label">上课地址</text>
        <text class="info-value">{{ order.address }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">单价</text>
        <text class="info-value">¥{{ order.unit_price }}/小时</text>
      </view>
      <view class="divider" />
      <view class="info-row total-row">
        <text class="info-label">订单金额</text>
        <text class="info-value amount">¥{{ order.total_amount ? order.total_amount.toFixed(2) : '0.00' }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-area" v-if="showActions">
      <u-button
        v-if="order.status === 'pending_settlement'"
        type="primary"
        shape="circle"
        size="large"
        @click="confirmComplete"
      >
        ✅ 满意，确认完成
      </u-button>
      <u-button
        v-if="order.status === 'pending_settlement'"
        type="error"
        plain
        shape="circle"
        size="large"
        class="mt-12"
        @click="requestRefund"
      >
        不满意，申请退款
      </u-button>
      <view v-if="order.status === 'pending_confirm'" class="status-hint">
        ⏳ 等待教师确认接单中...
      </view>
      <view v-if="order.status === 'pending_trial'" class="status-hint">
        📅 教师已接单，等待上课日期
      </view>
      <view v-if="order.status === 'completed'" class="status-hint success">
        ✅ 订单已完成，感谢使用河大家教
      </view>
      <view v-if="order.status === 'cancelled'" class="status-hint danger">
        ❌ 订单已取消
        <text v-if="order.cancel_reason" class="cancel-reason">
          （{{ order.cancel_reason }}）
        </text>
      </view>
    </view>

    <!-- 确认完成弹窗 -->
    <u-modal
      v-model="showConfirmModal"
      title="确认完成"
      content="确认后平台将自动结算给教师，结算金额为 ¥{{ order.settlement_amount ? order.settlement_amount.toFixed(2) : order.total_amount ? order.total_amount.toFixed(2) : '0.00' }}。确认后不可撤销。"
      show-cancel-button
      confirm-text="确认完成"
      cancel-text="再想想"
      @confirm="doConfirm"
    />
  </view>
</template>

<script>
import { fetchData, postData } from '@/utils/api.js'

export default {
  data() {
    return {
      order: {},
      showConfirmModal: false,
      loading: false,
    }
  },

  computed: {
    /**
     * 时间线数据
     * 优先使用API返回的timeline；否则根据status推导
     */
    timelineList() {
      if (this.order.timeline && this.order.timeline.length > 0) {
        return this.order.timeline.map(t => ({
          title: t.event,
          desc: t.time,
        }))
      }
      // 根据订单状态推导时间线
      return this.deriveTimeline()
    },

    /**
     * 当前进行到哪一步
     */
    timelineCurrent() {
      if (this.order.timeline && this.order.timeline.length > 0) {
        const doneCount = this.order.timeline.filter(t => t.status === 'done').length
        return doneCount - 1 >= 0 ? doneCount - 1 : 0
      }
      // 推导的时间线：取最后一项已完成的索引
      const list = this.deriveTimeline()
      const doneIdx = list.length - 1
      return Math.max(0, doneIdx > 0 ? doneIdx - 1 : 0)
    },

    /**
     * 是否显示操作按钮
     */
    showActions() {
      return [
        'pending_confirm', 'pending_trial', 'in_progress',
        'pending_settlement', 'completed', 'cancelled',
      ].includes(this.order.status)
    },
  },

  onLoad(options) {
    if (options.id) {
      this.loadOrder(options.id)
    }
  },

  methods: {
    /**
     * 加载订单详情 → GET /api/v1/orders/{order_id}
     */
    async loadOrder(orderId) {
      this.loading = true
      try {
        const data = await fetchData(`/api/v1/orders/${orderId}`, null, { showLoading: true, loadingText: '加载中...' })
        this.order = this.mapOrderData(data)
      } catch (err) {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    /**
     * 映射API返回的订单数据为页面需要格式
     */
    mapOrderData(data) {
      const statusColorMap = {
        pending_confirm: '#FF976A',
        pending_trial: '#1989FA',
        in_progress: '#1989FA',
        pending_settlement: '#FF976A',
        completed: '#07C160',
        cancelled: '#EE0A24',
        dispute: '#EE0A24',
      }
      const statusLabelMap = {
        pending_confirm: '待确认',
        pending_trial: '待试课',
        in_progress: '进行中',
        pending_settlement: '待结算',
        completed: '已完成',
        cancelled: '已取消',
        dispute: '纠纷中',
      }
      return {
        ...data,
        status_label: data.status_label || statusLabelMap[data.status] || data.status,
        status_color: data.status_color || statusColorMap[data.status] || '#999999',
      }
    },

    /**
     * 根据订单status推导时间线（无API timeline时使用）
     */
    deriveTimeline() {
      const status = this.order.status
      const lines = [
        { title: '订单已创建', desc: '等待教师确认接单' },
        { title: '教师已接单', desc: '等待上课日期' },
        { title: '课程进行中', desc: '教师按时授课' },
        { title: '家长确认完成', desc: '结算给教师' },
      ]
      const statusOrder = ['pending_confirm', 'pending_trial', 'in_progress', 'completed']
      const currentIdx = statusOrder.indexOf(status)
      if (currentIdx < 0) {
        // 已取消或其他状态：显示当前状态
        const labelMap = {
          pending_settlement: '家长确认完成',
          cancelled: '订单已取消',
          dispute: '订单纠纷中',
        }
        const label = labelMap[status] || status
        return [{ title: label, desc: '' }]
      }
      // 已完成：全部绿色
      if (status === 'completed') {
        return lines
      }
      // 其他状态：当前及之前为活跃
      return lines.slice(0, currentIdx + 1)
    },

    /**
     * 确认完成
     */
    confirmComplete() {
      this.showConfirmModal = true
    },

    /**
     * 执行确认完成 → POST /api/v1/orders/{order_id}/confirm
     */
    async doConfirm() {
      try {
        await postData(`/api/v1/orders/${this.order.order_id}/confirm`, null, {
          showLoading: true,
          loadingText: '处理中...',
        })
        uni.showToast({ title: '确认成功，感谢使用！', icon: 'success' })
        this.order.status = 'completed'
        this.order.status_label = '已完成'
        this.order.status_color = '#07C160'
        this.showConfirmModal = false
      } catch (err) {
        uni.showToast({ title: err.message || '确认失败', icon: 'none' })
      }
    },

    /**
     * 申请退款
     */
    requestRefund() {
      uni.showToast({ title: '退款功能将在P1阶段开放', icon: 'none' })
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

.timeline-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.info-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

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
      color: #EE0A24;
    }
  }
}

.divider {
  height: 1px;
  background: #EBEDF0;
  margin: 6px 0;
}

.action-area {
  margin-top: 20px;

  .mt-12 {
    margin-top: 12px;
  }

  .status-hint {
    text-align: center;
    color: #666666;
    font-size: 14px;
    padding: 16px;

    &.success {
      color: #07C160;
    }

    &.danger {
      color: #EE0A24;
    }

    .cancel-reason {
      font-size: 12px;
      color: #999999;
      display: block;
      margin-top: 4px;
    }
  }
}
</style>
