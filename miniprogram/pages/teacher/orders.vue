<template>
  <!-- 教师订单列表页 -->
  <view class="order-list-page">
    <!-- Tab切换 -->
    <u-tabs
      :list="tabs"
      :current="currentTab"
      @change="onTabChange"
      :activeStyle="{ color: '#07C160' }"
      lineColor="#07C160"
      :scrollable="true"
    />

    <!-- 订单列表 -->
    <view class="order-content">
      <view
        v-for="order in filteredOrders"
        :key="order.order_id"
        class="order-card"
      >
        <!-- 订单头部 -->
        <view class="order-header">
          <text class="order-no">{{ order.order_no }}</text>
          <view
            class="status-badge"
            :style="{ background: getStatusBg(order.status), color: getStatusColor(order.status) }"
          >
            {{ order.status_label }}
          </view>
        </view>

        <!-- 订单主体 -->
        <view class="order-body">
          <view class="order-info">
            <text class="order-parent">家长：{{ order.parent_name }}</text>
            <text class="order-subject">{{ order.subject }} · {{ order.grade }}</text>
            <text class="order-time">
              {{ order.lesson_date }} {{ order.start_time }}-{{ order.end_time }}
            </text>
            <text v-if="order.address" class="order-addr">📍 {{ order.address }}</text>
            <text v-if="order.parent_note" class="order-note">
              💬 备注：{{ order.parent_note }}
            </text>
          </view>
        </view>

        <!-- 订单底部 -->
        <view class="order-footer">
          <text class="order-amount">
            ¥{{ order.total_amount.toFixed(2) }}
            <text class="settlement-hint">
              （预计收入 ¥{{ order.settlement_amount.toFixed(2) }}）
            </text>
          </text>
          <view class="order-actions">
            <!-- 待确认：接受/拒绝 -->
            <template v-if="order.status === 'pending_confirm'">
              <u-button
                type="primary"
                size="mini"
                shape="circle"
                @click="handleAccept(order)"
              >
                确认接单
              </u-button>
              <u-button
                type="error"
                size="mini"
                shape="circle"
                plain
                @click="handleReject(order)"
              >
                拒绝
              </u-button>
            </template>
            <!-- 待试课：标记上课 -->
            <u-button
              v-if="order.status === 'pending_trial'"
              type="primary"
              size="mini"
              shape="circle"
              @click="handleStart(order)"
            >
              标记上课
            </u-button>
            <!-- 进行中：标记完成 -->
            <u-button
              v-if="order.status === 'in_progress'"
              type="primary"
              size="mini"
              shape="circle"
              @click="handleComplete(order)"
            >
              标记完成
            </u-button>
            <!-- 已完成 -->
            <text v-if="order.status === 'completed'" class="done-text">✅ 已完成</text>
            <!-- 查看详情 -->
            <text class="detail-link" @click="goDetail(order.order_id)">详情 ></text>
          </view>
        </view>
      </view>

      <u-empty
        v-if="filteredOrders.length === 0"
        text="暂无订单"
        mode="list"
        margin-top="80"
      />
    </view>

    <!-- 拒绝原因弹窗 -->
    <u-modal
      v-model="showRejectModal"
      title="拒绝接单"
      content="请填写拒绝原因"
      show-cancel-button
      confirm-text="确认拒绝"
      cancel-text="取消"
      @confirm="doReject"
    >
      <view slot="default" class="reject-input-wrapper">
        <u-input
          v-model="rejectReason"
          placeholder="请输入拒绝原因（选填）"
          border="surround"
        />
      </view>
    </u-modal>
  </view>
</template>

<script>
import {
  teacherOrderTabs,
  orderStatusMap,
} from '@/common/mock.js'
import { getPaginated, postData } from '@/utils/api.js'

export default {
  data() {
    return {
      tabs: teacherOrderTabs,
      currentTab: 0,
      orders: [],
      showRejectModal: false,
      rejectReason: '',
      currentRejectOrder: null,
      loading: false,
      page: 1,
      total: 0,
    }
  },

  computed: {
    filteredOrders() {
      return this.orders
    },
  },

  onLoad() {
    this.loadOrders()
  },

  methods: {
    onTabChange(e) {
      this.currentTab = e.index
      this.page = 1
      this.orders = []
      this.loadOrders()
    },

    getStatusColor(status) {
      return orderStatusMap[status]?.color || '#999999'
    },

    getStatusBg(status) {
      return orderStatusMap[status]?.bg || '#F5F5F5'
    },

    /**
     * 加载订单
     */
    async loadOrders() {
      if (this.loading) return
      this.loading = true
      try {
        const tabValue = this.tabs[this.currentTab].value
        const params = {
          page: this.page,
          page_size: 20,
        }
        if (tabValue !== 'all') {
          params.status = tabValue
        }
        const result = await getPaginated('/api/v1/orders', params)
        if (this.page === 1) {
          this.orders = result.items
        } else {
          this.orders = this.orders.concat(result.items)
        }
        this.total = result.total
      } catch (e) {
        // error already toasted by api util
      } finally {
        this.loading = false
      }
    },

    /**
     * 确认接单
     */
    async handleAccept(order) {
      uni.showModal({
        title: '确认接单',
        content: `确认接受订单 ${order.order_no}？`,
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${order.order_id}/accept`)
              uni.showToast({ title: '已接单', icon: 'success' })
              this.loadOrders()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    /**
     * 拒绝接单
     */
    handleReject(order) {
      this.currentRejectOrder = order
      this.rejectReason = ''
      this.showRejectModal = true
    },

    /**
     * 执行拒绝
     */
    async doReject() {
      if (!this.currentRejectOrder) return
      try {
        await postData(`/api/v1/orders/${this.currentRejectOrder.order_id}/reject`, {
          reason: this.rejectReason || '教师拒绝接单',
        })
        uni.showToast({ title: '已拒绝', icon: 'none' })
        this.loadOrders()
      } catch (e) {
        // error handled by api util
      }
      this.showRejectModal = false
    },

    /**
     * 标记上课
     */
    async handleStart(order) {
      uni.showModal({
        title: '标记上课',
        content: '确认该订单已开始上课？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${order.order_id}/start`)
              uni.showToast({ title: '已标记上课', icon: 'success' })
              this.loadOrders()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    /**
     * 标记完成
     */
    async handleComplete(order) {
      uni.showModal({
        title: '标记完成',
        content: '确认该订单已完成上课？标记后等待家长确认。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/orders/${order.order_id}/complete`)
              uni.showToast({ title: '已标记完成', icon: 'success' })
              this.loadOrders()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },

    /**
     * 查看详情
     */
    goDetail(orderId) {
      uni.navigateTo({
        url: `/pages/teacher/order-detail?id=${orderId}`,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.order-list-page {
  background: #F5F5F5;
  min-height: 100vh;
}

.order-content {
  padding: 10px 12px;
}

.order-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .order-no {
      font-size: 12px;
      color: #999999;
    }

    .status-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 500;
    }
  }

  .order-body {
    .order-info {
      .order-parent {
        font-size: 14px;
        font-weight: 600;
        color: #1A1A1A;
        display: block;
      }

      .order-subject {
        font-size: 13px;
        color: #666666;
        display: block;
        margin: 3px 0;
      }

      .order-time {
        font-size: 12px;
        color: #666666;
        display: block;
      }

      .order-addr {
        font-size: 12px;
        color: #999999;
        display: block;
        margin-top: 2px;
      }

      .order-note {
        font-size: 12px;
        color: #FF976A;
        display: block;
        margin-top: 4px;
        background: #FFF7EE;
        padding: 4px 8px;
        border-radius: 4px;
      }
    }
  }

  .order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid #F0F0F0;

    .order-amount {
      font-size: 14px;
      font-weight: 600;
      color: #EE0A24;

      .settlement-hint {
        font-size: 10px;
        color: #999999;
        font-weight: 400;
      }
    }

    .order-actions {
      display: flex;
      align-items: center;
      gap: 8px;

      .done-text {
        font-size: 13px;
        color: #07C160;
      }

      .detail-link {
        font-size: 12px;
        color: #1989FA;
      }
    }
  }
}

.reject-input-wrapper {
  padding: 16px 0;
}
</style>
