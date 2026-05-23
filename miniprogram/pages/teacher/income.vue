<template>
  <!-- 教师收入管理页 -->
  <view class="income-page">
    <!-- 收入概览 -->
    <view class="income-summary">
      <view class="income-card primary">
        <text class="income-label">可提现余额</text>
        <text class="income-value">¥{{ income.withdrawable_balance.toFixed(2) }}</text>
      </view>
      <view class="income-card">
        <text class="income-label">累计收入</text>
        <text class="income-value">¥{{ income.total_income.toFixed(2) }}</text>
      </view>
      <view class="income-card">
        <text class="income-label">待结算</text>
        <text class="income-value warn">¥{{ income.pending_income.toFixed(2) }}</text>
      </view>
    </view>

    <!-- 提现按钮 -->
    <view class="withdraw-section">
      <u-button
        type="primary"
        shape="circle"
        size="large"
        @click="handleWithdraw"
        :disabled="income.withdrawable_balance < 10"
      >
        提现
      </u-button>
      <text class="withdraw-hint">最低提现金额 ¥10.00</text>
    </view>

    <!-- 收入明细 -->
    <view class="section">
      <view class="section-title">收入明细</view>
      <view
        v-for="record in records"
        :key="record.record_id"
        class="record-item"
      >
        <view class="record-header">
          <text class="record-order-no">{{ record.order_no }}</text>
          <text class="record-status">{{ record.status }}</text>
        </view>
        <view class="record-body">
          <text class="record-subject">{{ record.subject }} · {{ record.grade }}</text>
          <text class="record-date">{{ record.lesson_date }} 上课</text>
        </view>
        <view class="record-footer">
          <view class="record-breakdown">
            <text class="breakdown-item">课时费 ¥{{ record.total_amount.toFixed(2) }}</text>
            <text class="breakdown-item minus">平台佣金 -¥{{ record.commission_amount.toFixed(2) }}</text>
          </view>
          <text class="record-amount">¥{{ record.settlement_amount.toFixed(2) }}</text>
        </view>
      </view>

      <u-empty
        v-if="records.length === 0"
        text="暂无收入记录"
        mode="list"
      />
    </view>
  </view>
</template>

<script>
import { fetchData, getPaginated, postData } from '@/utils/api.js'

export default {
  data() {
    return {
      income: {
        withdrawable_balance: 0,
        total_income: 0,
        pending_income: 0,
      },
      records: [],
    }
  },

  async onLoad() {
    await this.loadIncome()
  },

  methods: {
    /**
     * 加载收入数据
     */
    async loadIncome() {
      try {
        const income = await fetchData('/api/v1/teacher/income')
        this.income = income
      } catch (e) {
        // error handled by api util
      }

      try {
        const result = await getPaginated('/api/v1/teacher/income/records', {
          page: 1,
          page_size: 50,
        })
        this.records = result.items
      } catch (e) {
        // error handled by api util
      }
    },

    /**
     * 提现
     */
    async handleWithdraw() {
      if (this.income.withdrawable_balance < 10) {
        uni.showToast({ title: '余额不足最低提现金额', icon: 'none' })
        return
      }

      uni.showModal({
        title: '确认提现',
        content: `确认提现 ¥${this.income.withdrawable_balance.toFixed(2)} 到微信零钱？`,
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData('/api/v1/teacher/withdraw', {
                amount: this.income.withdrawable_balance,
              })
              uni.showToast({
                title: '提现申请已提交，等待审核',
                icon: 'success',
              })
              this.loadIncome()
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
.income-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding: 12px;
}

.income-summary {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;

  .income-card {
    flex: 1;
    background: #FFFFFF;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

    &.primary {
      background: linear-gradient(135deg, #07C160, #06AD56);

      .income-label,
      .income-value {
        color: #FFFFFF;
      }
    }

    .income-label {
      font-size: 11px;
      color: #999999;
      display: block;
      margin-bottom: 6px;
    }

    .income-value {
      font-size: 18px;
      font-weight: 700;
      color: #1A1A1A;
      display: block;

      &.warn {
        color: #FF976A;
      }
    }
  }
}

.withdraw-section {
  padding: 0 0 16px;
  text-align: center;

  .withdraw-hint {
    font-size: 12px;
    color: #999999;
    margin-top: 8px;
    display: block;
  }
}

.section {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: #1A1A1A;
    margin-bottom: 12px;
  }
}

.record-item {
  padding: 10px 0;
  border-bottom: 1px solid #F0F0F0;

  &:last-child {
    border-bottom: none;
  }

  .record-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;

    .record-order-no {
      font-size: 13px;
      color: #1A1A1A;
      font-weight: 500;
    }

    .record-status {
      font-size: 11px;
      color: #07C160;
      background: #E8F8EF;
      padding: 2px 6px;
      border-radius: 4px;
    }
  }

  .record-body {
    font-size: 12px;
    color: #999999;
    margin-bottom: 6px;

    .record-subject {
      margin-right: 8px;
    }
  }

  .record-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .record-breakdown {
      .breakdown-item {
        font-size: 11px;
        color: #666666;
        display: block;

        &.minus {
          color: #EE0A24;
        }
      }
    }

    .record-amount {
      font-size: 16px;
      font-weight: 700;
      color: #07C160;
    }
  }
}
</style>
