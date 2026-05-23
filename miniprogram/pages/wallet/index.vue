<template>
  <!-- 虚拟币钱包页 -->
  <view class="wallet-page">
    <!-- 余额卡片 -->
    <view class="balance-card">
      <text class="balance-label">我的虚拟币余额</text>
      <text class="balance-amount">{{ wallet.balance }}</text>
      <text class="balance-unit">币（1币 = ¥1）</text>
      <view class="balance-stats">
        <text class="stat-item">累计充值 {{ wallet.total_recharged }}币</text>
        <text class="stat-sep">|</text>
        <text class="stat-item">累计消费 {{ wallet.total_spent }}币</text>
      </view>
    </view>

    <!-- 充值套餐 -->
    <view class="section">
      <view class="section-title">充值套餐</view>
      <view class="package-list">
        <view
          v-for="pkg in packages"
          :key="pkg.id"
          class="package-item"
          :class="{ popular: pkg.popular }"
          @click="handleRecharge(pkg)"
        >
          <view v-if="pkg.popular" class="popular-tag">推荐</view>
          <text class="package-coins">{{ pkg.coins }}币</text>
          <text class="package-price">{{ pkg.label }}</text>
        </view>
      </view>
    </view>

    <!-- 消费记录 -->
    <view class="section">
      <view class="section-title">消费记录</view>
      <view
        v-for="tx in transactions"
        :key="tx.transaction_id"
        class="tx-item"
      >
        <view class="tx-left">
          <text class="tx-desc">{{ tx.description }}</text>
          <text class="tx-date">{{ tx.created_at.slice(0, 10) }}</text>
        </view>
        <text
          class="tx-amount"
          :class="{ income: tx.amount > 0, expense: tx.amount < 0 }"
        >
          {{ tx.amount > 0 ? '+' : '' }}{{ tx.amount }}币
        </text>
      </view>

      <u-empty
        v-if="transactions.length === 0"
        text="暂无消费记录"
        mode="list"
      />
    </view>
  </view>
</template>

<script>
import {
  mockRechargePackages,
} from '@/common/mock.js'
import { fetchData, getPaginated, postData } from '@/utils/api.js'

export default {
  data() {
    return {
      wallet: {
        balance: 0,
        total_recharged: 0,
        total_spent: 0,
      },
      transactions: [],
      packages: mockRechargePackages,
    }
  },

  onLoad() {
    this.loadWallet()
  },

  onShow() {
    this.loadWallet()
  },

  methods: {
    /**
     * 加载钱包数据
     */
    async loadWallet() {
      try {
        const wallet = await fetchData('/api/v1/wallet')
        this.wallet = wallet
      } catch (e) {
        // error handled by api util
      }

      try {
        const result = await getPaginated('/api/v1/wallet/transactions', {
          page: 1,
          page_size: 50,
        })
        this.transactions = result.items.map(tx => ({
          ...tx,
          // 充值正数，消费负数，适配模板显示
          amount: tx.type === 'recharge' ? Math.abs(tx.amount) : -Math.abs(tx.amount),
        }))
      } catch (e) {
        // error handled by api util
      }
    },

    /**
     * 充值
     */
    async handleRecharge(pkg) {
      uni.showModal({
        title: '确认充值',
        content: `确认充值 ${pkg.label} 吗？`,
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData('/api/v1/wallet/recharge', {
                amount: pkg.amount,
                coins: pkg.coins,
              })
              uni.showToast({ title: '充值成功！', icon: 'success' })
              this.loadWallet()
            } catch (e) {
              // error handled by api util
            }
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.wallet-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding: 12px;
}

.balance-card {
  background: linear-gradient(135deg, #07C160, #06AD56);
  border-radius: 12px;
  padding: 24px;
  color: #FFFFFF;
  text-align: center;
  margin-bottom: 12px;

  .balance-label {
    font-size: 14px;
    opacity: 0.85;
  }

  .balance-amount {
    font-size: 36px;
    font-weight: 700;
    display: block;
    margin: 8px 0;
  }

  .balance-unit {
    font-size: 12px;
    opacity: 0.7;
  }

  .balance-stats {
    margin-top: 12px;
    font-size: 12px;
    opacity: 0.8;

    .stat-item {
      margin: 0 4px;
    }

    .stat-sep {
      margin: 0 8px;
    }
  }
}

.section {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: #1A1A1A;
    margin-bottom: 12px;
  }
}

.package-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;

  .package-item {
    background: #F9FAFB;
    border: 1.5px solid #EBEDF0;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    position: relative;

    &.popular {
      border-color: #07C160;
      background: #E8F8EF;
    }

    .popular-tag {
      position: absolute;
      top: 0;
      right: 0;
      background: #07C160;
      color: #FFFFFF;
      font-size: 10px;
      padding: 2px 8px;
      border-radius: 0 8px 0 8px;
    }

    .package-coins {
      font-size: 20px;
      font-weight: 700;
      color: #1A1A1A;
      display: block;
    }

    .package-price {
      font-size: 13px;
      color: #666666;
      margin-top: 4px;
      display: block;
    }
  }
}

.tx-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #F0F0F0;

  &:last-child {
    border-bottom: none;
  }

  .tx-left {
    .tx-desc {
      font-size: 14px;
      color: #1A1A1A;
      display: block;
    }

    .tx-date {
      font-size: 12px;
      color: #999999;
      margin-top: 2px;
      display: block;
    }
  }

  .tx-amount {
    font-size: 14px;
    font-weight: 600;

    &.income {
      color: #07C160;
    }

    &.expense {
      color: #EE0A24;
    }
  }
}
</style>
