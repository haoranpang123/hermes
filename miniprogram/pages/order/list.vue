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
        v-for="order in filteredOrders"
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
            <text class="avatar-text">{{ order.teacher_initial || order.teacher_name[0] }}</text>
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
            ¥{{ order.total_amount.toFixed(2) }}
          </text>
          <view class="order-actions">
            <text class="action-link">查看详情 ></text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <u-empty
        v-if="filteredOrders.length === 0"
        text="暂无订单"
        mode="list"
        margin-top="80"
      />
    </view>
  </view>
</template>

<script>
import { mockOrders, orderStatusMap, parentOrderTabs } from '@/common/mock.js'

export default {
  data() {
    return {
      tabs: parentOrderTabs,
      currentTab: 0,
      orders: mockOrders,
    }
  },

  computed: {
    /**
     * 根据当前Tab筛选订单
     */
    filteredOrders() {
      const tabValue = this.tabs[this.currentTab].value
      if (tabValue === 'all') return this.orders

      // 'active' 包含待试课+进行中+待结算
      if (tabValue === 'active') {
        return this.orders.filter(o =>
          ['pending_trial', 'in_progress', 'pending_settlement'].includes(o.status)
        )
      }

      return this.orders.filter(o => o.status === tabValue)
    },
  },

  methods: {
    /**
     * Tab切换
     */
    onTabChange(e) {
      this.currentTab = e.index
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

  onPullDownRefresh() {
    // 模拟刷新
    setTimeout(() => {
      uni.stopPullDownRefresh()
    }, 500)
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
