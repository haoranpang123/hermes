<template>
  <!-- 教师详情页 -->
  <view class="detail-page">
    <!-- 教师头部信息 -->
    <view class="detail-header">
      <view
        class="big-avatar"
        :style="{ background: teacher.avatar_bg || 'linear-gradient(135deg, #07C160, #06AD56)' }"
      >
        <text class="avatar-text">{{ teacher.initial || teacher.nickname[0] }}</text>
      </view>
      <view class="header-info">
        <text class="teacher-name">{{ teacher.nickname }}</text>
        <text class="teacher-meta">
          {{ teacher.university }} · {{ teacher.major }} · {{ teacher.grade }}
        </text>
        <view class="teacher-stars">
          <text class="stars-icon">⭐</text>
          <text class="stars-value">{{ teacher.avg_rating }}</text>
          <text class="stars-count">（{{ teacher.review_count }}条评价）</text>
        </view>
      </view>
    </view>

    <!-- 基本信息区 -->
    <view class="detail-section">
      <view class="section-row">
        <text class="section-label">💰 课时费</text>
        <text class="section-value price-value">¥{{ teacher.min_price }}/小时</text>
      </view>
      <view class="section-row">
        <text class="section-label">📍 授课区域</text>
        <text class="section-value">{{ teacher.teaching_regions.join('、') }}</text>
      </view>
      <view class="section-row">
        <text class="section-label">👤 性别</text>
        <text class="section-value">{{ teacher.gender === 'male' ? '男' : '女' }}</text>
      </view>
    </view>

    <!-- 教学科目 -->
    <view class="detail-section">
      <view class="section-title">📋 教学科目</view>
      <view class="subject-tags">
        <u-tag
          v-for="(subject, idx) in teacher.subjects"
          :key="idx"
          :text="subject"
          type="primary"
          plain
          size="small"
          class="subject-tag"
        />
      </view>
    </view>

    <!-- 个人简介 -->
    <view class="detail-section">
      <view class="section-title">📝 个人简介</view>
      <text class="bio-text">{{ teacher.bio }}</text>
    </view>

    <!-- 资质证书 -->
    <view class="detail-section" v-if="teacher.certificates && teacher.certificates.length > 0">
      <view class="section-title">🎓 资质证书</view>
      <scroll-view scroll-x class="cert-scroll">
        <view class="cert-row">
          <view
            v-for="(cert, idx) in teacher.certificates"
            :key="idx"
            class="cert-item"
            @click="viewCertificate(cert)"
          >
            <view class="cert-thumb">
              <text class="cert-icon">📄</text>
            </view>
            <text class="cert-label">{{ cert.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 可预约时间 -->
    <view class="detail-section" v-if="teacher.schedules && teacher.schedules.length > 0">
      <view class="section-title">📅 可预约时间</view>
      <view class="schedule-list">
        <view
          v-for="(slot, idx) in teacher.schedules"
          :key="idx"
          class="schedule-item"
        >
          <text class="schedule-day">{{ slot.day_name }}</text>
          <text
            class="schedule-time"
            :class="{ booked: slot.status === 'booked' }"
          >
            {{ slot.start_time }} - {{ slot.end_time }}
          </text>
          <text class="schedule-status" :style="{ color: slot.status === 'available' ? '#07C160' : '#EE0A24' }">
            {{ slot.status === 'available' ? '可预约' : '已预约' }}
          </text>
        </view>
      </view>
    </view>

    <!-- 家长评价 -->
    <view class="detail-section" v-if="teacher.reviews && teacher.reviews.length > 0">
      <view class="section-title flex-between">
        <text>⭐ 家长评价（{{ teacher.review_count }}条）</text>
        <text class="view-all" @click="viewAllReviews">查看全部 ></text>
      </view>
      <view
        v-for="(review, idx) in teacher.reviews.slice(0, 2)"
        :key="idx"
        class="review-item"
      >
        <view class="review-header">
          <text class="review-name">{{ review.parent_nickname }}</text>
          <text class="review-date">{{ review.created_at.slice(0, 10) }}</text>
        </view>
        <view class="review-content">{{ review.content }}</view>
        <view class="review-scores">
          <text class="score-item">教学 {{ review.teaching_ability }}⭐</text>
          <text class="score-item">沟通 {{ review.communication }}⭐</text>
          <text class="score-item">准时 {{ review.punctuality }}⭐</text>
        </view>
      </view>
    </view>

    <!-- 底部占位（避免被按钮遮挡） -->
    <view style="height: 80px" />

    <!-- 底部操作栏 -->
    <view class="bottom-bar safe-bottom">
      <view class="btn-favorite" @click="toggleFavorite">
        <text :style="{ color: isFavorited ? '#EE0A24' : '#666666' }">
          {{ isFavorited ? '❤' : '♡' }}
        </text>
        <text class="btn-label">{{ isFavorited ? '已收藏' : '收藏' }}</text>
      </view>
      <u-button type="primary" plain shape="circle" size="small" @click="handleContact">
        💬 联系教师
      </u-button>
      <u-button type="primary" shape="circle" @click="handleBook">
        📅 立即预约
      </u-button>
    </view>

    <!-- 联系教师弹窗 -->
    <u-modal
      v-model="showContactModal"
      title="查看联系方式"
      :content="contactModalContent"
      show-cancel-button
      confirm-text="确认查看"
      cancel-text="取消"
      @confirm="confirmContact"
    />

    <!-- 虚拟币不足弹窗 -->
    <u-modal
      v-model="showCoinModal"
      title="虚拟币不足"
      :content="coinModalContent"
      show-cancel-button
      confirm-text="去充值"
      cancel-text="取消"
      @confirm="goToWallet"
    />
  </view>
</template>

<script>
import { mockTeacherDetail, mockWallet } from '@/common/mock.js'

export default {
  data() {
    return {
      teacher: {},
      isFavorited: false,
      showContactModal: false,
      showCoinModal: false,
      contactModalContent: '',
      coinModalContent: '',
      teacherId: null,
    }
  },

  onLoad(options) {
    if (options.id) {
      this.teacherId = parseInt(options.id)
      this.loadTeacherDetail(options.id)
    }
  },

  methods: {
    /**
     * 加载教师详情
     * 后续替换为 GET /teachers/{teacher_id}
     */
    loadTeacherDetail(id) {
      // 模拟API延迟
      setTimeout(() => {
        // 根据ID返回不同数据
        if (parseInt(id) === 1) {
          this.teacher = { ...mockTeacherDetail }
        } else {
          // 其他ID使用基础数据+部分mock数据
          this.teacher = {
            ...mockTeacherDetail,
            teacher_id: parseInt(id),
          }
        }
        this.isFavorited = this.teacher.is_favorited || false
      }, 200)
    },

    /**
     * 收藏/取消收藏
     */
    toggleFavorite() {
      this.isFavorited = !this.isFavorited
      const msg = this.isFavorited ? '已收藏' : '已取消收藏'
      uni.showToast({ title: msg, icon: 'none' })
    },

    /**
     * 联系教师（消耗虚拟币）
     */
    handleContact() {
      const coinCost = 5 // MVP固定5币
      const currentBalance = mockWallet.balance

      if (currentBalance < coinCost) {
        this.coinModalContent = `查看教师联系方式需要${coinCost}个虚拟币，当前余额${currentBalance}币，余额不足。`
        this.showCoinModal = true
        return
      }

      this.contactModalContent = `查看教师联系方式需消耗 ${coinCost} 个虚拟币（约¥${coinCost}），7天内再次查看不重复收费。是否继续？`
      this.showContactModal = true
    },

    /**
     * 确认查看联系方式
     */
    confirmContact() {
      // 模拟扣除虚拟币
      uni.showToast({
        title: '联系方式：138****1234',
        icon: 'none',
        duration: 3000,
      })
      this.showContactModal = false
    },

    /**
     * 跳转到钱包充值
     */
    goToWallet() {
      this.showCoinModal = false
      uni.navigateTo({ url: '/pages/wallet/index' })
    },

    /**
     * 立即预约 — 跳转到下单页
     */
    handleBook() {
      uni.navigateTo({
        url: `/pages/order/create?teacher_id=${this.teacherId}&subject=${this.teacher.subjects[0] || ''}&price=${this.teacher.min_price}`,
      })
    },

    /**
     * 查看证书大图
     */
    viewCertificate(cert) {
      uni.showToast({ title: '查看' + cert.label, icon: 'none' })
    },

    /**
     * 查看全部评价
     */
    viewAllReviews() {
      uni.showToast({ title: '查看全部评价（P1功能）', icon: 'none' })
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

.detail-header {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  .big-avatar {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    margin: 0 auto 12px;
    display: flex;
    align-items: center;
    justify-content: center;

    .avatar-text {
      font-size: 28px;
      font-weight: 700;
      color: #FFFFFF;
    }
  }

  .header-info {
    .teacher-name {
      font-size: 18px;
      font-weight: 700;
      color: #1A1A1A;
      display: block;
    }

    .teacher-meta {
      font-size: 12px;
      color: #666666;
      margin: 4px 0;
      display: block;
    }

    .teacher-stars {
      margin-top: 4px;
      font-size: 14px;

      .stars-icon {
        color: #FF9500;
      }

      .stars-value {
        font-weight: 600;
        color: #FF9500;
        margin-left: 4px;
      }

      .stars-count {
        font-size: 12px;
        color: #999999;
        margin-left: 2px;
      }
    }
  }
}

.detail-section {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 10px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .view-all {
    font-size: 12px;
    color: #1989FA;
    font-weight: 400;
  }
}

.section-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 14px;

  .section-label {
    color: #666666;
  }

  .section-value {
    color: #1A1A1A;
    font-weight: 500;
  }

  .price-value {
    color: #EE0A24;
    font-weight: 600;
  }
}

.subject-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;

  .subject-tag {
    margin: 0;
  }
}

.bio-text {
  font-size: 14px;
  color: #666666;
  line-height: 1.6;
  white-space: pre-line;
}

.cert-scroll {
  white-space: nowrap;

  .cert-row {
    display: inline-flex;
    gap: 10px;

    .cert-item {
      width: 80px;
      text-align: center;

      .cert-thumb {
        width: 80px;
        height: 60px;
        border-radius: 6px;
        background: #F0F0F0;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #EBEDF0;
        margin-bottom: 4px;

        .cert-icon {
          font-size: 24px;
        }
      }

      .cert-label {
        font-size: 10px;
        color: #999999;
      }
    }
  }
}

.schedule-list {
  .schedule-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #F0F0F0;

    &:last-child {
      border-bottom: none;
    }

    .schedule-day {
      font-size: 14px;
      font-weight: 500;
      color: #1A1A1A;
      width: 50px;
    }

    .schedule-time {
      font-size: 14px;
      color: #07C160;
      flex: 1;

      &.booked {
        color: #EE0A24;
        text-decoration: line-through;
      }
    }

    .schedule-status {
      font-size: 12px;
    }
  }
}

.review-item {
  padding: 10px 0;
  border-bottom: 1px solid #F0F0F0;

  &:last-child {
    border-bottom: none;
  }

  .review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;

    .review-name {
      font-size: 14px;
      font-weight: 600;
      color: #1A1A1A;
    }

    .review-date {
      font-size: 12px;
      color: #999999;
    }
  }

  .review-content {
    font-size: 13px;
    color: #666666;
    line-height: 1.5;
    margin-bottom: 6px;
  }

  .review-scores {
    font-size: 12px;
    color: #FF9500;

    .score-item {
      margin-right: 12px;
    }
  }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #FFFFFF;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-top: 1px solid #F0F0F0;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.04);

  .btn-favorite {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 20px;
    flex-shrink: 0;

    .btn-label {
      font-size: 10px;
    }
  }

  .u-button {
    margin: 0;
  }
}

.safe-bottom {
  padding-bottom: calc(10px + env(safe-area-inset-bottom, 0));
}
</style>
