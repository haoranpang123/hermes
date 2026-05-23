<template>
  <!-- 订单列表页：Tab切换 + 订单卡片列表 -->
  <view class="order-list-page">
    <!-- Tab 切换 -->
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
        v-for="order in orders"
        :key="order.order_id"
        class="order-card"
        @click="goToDetail(order.order_id)"
      >
        <!-- 订单头部 -->
        <view class="order-header">
          <text class="order-no">订单号：{{ order.order_no }}</text>
          <view
            class="order-status-badge"
            :style="{
              background: getStatusConfig(order.status).bg,
              color: getStatusConfig(order.status).color,
            }"
          >
            {{ getStatusConfig(order.status).label }}
          </view>
        </view>

        <!-- 订单主体 -->
        <view class="order-body">
          <view
            class="order-avatar"
            :style="{ background: order.teacher_avatar_bg || '#E0E0E0' }"
          >
            <text class="avatar-text">{{ order.teacher_initial || (order.teacher_name && order.teacher_name[0]) || '老' }}</text>
          </view>
          <view class="order-info">
            <text class="order-teacher">{{ order.teacher_name }}</text>
            <text class="order-subject">{{ order.subject }} · {{ order.grade }}</text>
            <text class="order-time">
              {{ order.lesson_date }} {{ order.start_time }}-{{ order.end_time }}
              ({{ order.duration }}小时)
            </text>
          </view>
        </view>

        <!-- 订单底部 -->
        <view class="order-footer">
          <text class="order-amount">
            ¥{{ order.total_amount ? order.total_amount.toFixed(2) : '0.00' }}
          </text>
          <view class="order-actions">
            <text class="action-link">查看详情 ></text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <u-empty
        v-if="!loading && orders.length === 0"
        text="暂无订单"
        mode="list"
        margin-top="80"
      />
    </view>
  </view>
</template>

<script>
import { getPaginated } from '@/utils/api.js'
import { orderStatusMap, parentOrderTabs } from '@/common/mock.js'

export default {
  data() {
    return {
      tabs: parentOrderTabs,
      currentTab: 0,
      orders: [],
      loading: false,
      page: 1,
      pageSize: 20,
      total: 0,
      hasMore: true,
    }
  },

  onLoad() {
    this.fetchOrders()
  },

  onShow() {
    // 每次回到列表页时刷新（可能从详情页返回，状态有变化）
    this.page = 1
    this.hasMore = true
    this.fetchOrders()
  },

  onPullDownRefresh() {
    this.page = 1
    this.hasMore = true
    this.fetchOrders().finally(() => {
      uni.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.hasMore && !this.loading) {
      this.page++
      this.fetchOrders(true)
    }
  },

  methods: {
    /**
     * 获取当前Tab对应的status筛选值
     */
    getFilterStatus() {
      const tabValue = this.tabs[this.currentTab].value
      if (tabValue === 'all') return undefined
      if (tabValue === 'active') return 'active' // 后端处理进行中聚合
      return tabValue
    },

    /**
     * 从API拉取订单列表
     */
    async fetchOrders(append = false) {
      this.loading = true
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
        }
        const status = this.getFilterStatus()
        if (status) {
          params.status = status
        }

        const result = await getPaginated('/api/v1/orders', params, { showLoading: !append })
        const items = result.items

        if (append) {
          this.orders = [...this.orders, ...items]
        } else {
          this.orders = items
        }
        this.total = result.total
        this.hasMore = this.orders.length < this.total
      } catch (err) {
        if (!append) {
          this.orders = []
        }
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    /**
     * Tab切换
     */
    onTabChange(e) {
      this.currentTab = e.index
      this.page = 1
      this.hasMore = true
      this.fetchOrders()
    },

    /**
     * 获取状态配置
     */
    getStatusConfig(status) {
      return orderStatusMap[status] || { label: status, color: '#999999', bg: '#F5F5F5' }
    },

    /**
     * 跳转订单详情
     */
    goToDetail(orderId) {
      uni.navigateTo({
        url: `/pages/order/detail?id=${orderId}`,
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

    .order-status-badge {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 500;
    }
  }

  .order-body {
    display: flex;
    gap: 10px;

    .order-avatar {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;

      .avatar-text {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
      }
    }

    .order-info {
      flex: 1;

      .order-teacher {
        font-size: 14px;
        font-weight: 600;
        color: #1A1A1A;
        display: block;
      }

      .order-subject {
        font-size: 12px;
        color: #666666;
        display: block;
        margin: 2px 0;
      }

      .order-time {
        font-size: 12px;
        color: #999999;
        display: block;
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
    }

    .order-actions {
      .action-link {
        font-size: 12px;
        color: #1989FA;
      }
    }
  }
}
</style>
