<template>
  <!-- 首页：搜索栏 + 筛选 + 教师卡片列表 -->
  <view class="home-page">
    <!-- 搜索栏 -->
    <view class="search-wrapper">
      <u-search
        v-model="keyword"
        placeholder="搜索教师/科目/学校..."
        :show-action="false"
        shape="round"
        bg-color="#FFFFFF"
        @search="onSearch"
        @clear="onClear"
      />
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar">
      <u-dropdown ref="dropdown" :close-on-click-mask="true">
        <u-dropdown-item
          v-model="filters.subject"
          :title="filters.subject || '科目'"
          :options="subjectOptions"
          @change="onFilterChange"
        />
        <u-dropdown-item
          v-model="filters.grade"
          :title="filters.grade || '年级'"
          :options="gradeOptions"
          @change="onFilterChange"
        />
        <u-dropdown-item
          v-model="filters.region"
          :title="filters.region || '地区'"
          :options="regionOptions"
          @change="onFilterChange"
        />
      </u-dropdown>
    </view>

    <!-- 教师列表（下拉刷新+上拉加载） -->
    <view class="teacher-list">
      <view
        v-for="teacher in teacherList"
        :key="teacher.teacher_id"
        class="teacher-card"
        @click="goToDetail(teacher.teacher_id)"
      >
        <!-- 头像 -->
        <view class="teacher-avatar" :style="{ background: teacher.avatar_bg || '#E0E0E0' }">
          <text class="avatar-text">{{ teacher.initial || teacher.nickname[0] }}</text>
        </view>

        <!-- 信息区 -->
        <view class="teacher-info">
          <!-- 姓名 + 评分 -->
          <view class="info-name-row">
            <text class="info-name">{{ teacher.nickname }}</text>
            <view class="info-rating">
              <text class="rating-star">⭐</text>
              <text class="rating-value">{{ teacher.avg_rating }}</text>
              <text class="rating-count">({{ teacher.review_count }})</text>
            </view>
          </view>

          <!-- 学校专业年级 -->
          <view class="info-school">
            {{ teacher.university }} · {{ teacher.major }} · {{ teacher.grade }}
          </view>

          <!-- 科目标签 -->
          <view class="info-tags">
            <u-tag
              v-for="(subject, idx) in teacher.subjects"
              :key="idx"
              :text="subject"
              type="info"
              plain
              size="mini"
              class="subject-tag"
            />
          </view>

          <!-- 价格 -->
          <view class="info-bottom">
            <view class="info-price">
              <text class="price-value">¥{{ teacher.min_price }}</text>
              <text class="price-unit">/小时</text>
            </view>
            <view class="info-region">
              <text class="region-text">{{ teacher.teaching_regions.slice(0, 2).join('、') }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <u-empty
        v-if="teacherList.length === 0 && !loading"
        text="暂无符合条件的教师"
        mode="list"
        margin-top="80"
      />

      <!-- 加载更多 -->
      <u-loadmore
        v-if="teacherList.length > 0"
        :status="loadStatus"
        :loading-text="'加载中...'"
        :nomore-text="'— 没有更多了 —'"
        margin-bottom="20"
      />
    </view>
  </view>
</template>

<script>
import { mockTeachers, mockFilterOptions } from '@/common/mock.js'

export default {
  data() {
    return {
      keyword: '',
      filters: {
        subject: '',
        grade: '',
        region: '',
      },
      teacherList: [],
      page: 1,
      pageSize: 10,
      loading: false,
      loadStatus: 'loadmore', // loadmore | loading | nomore

      // 筛选选项
      subjectOptions: [
        { label: '全部科目', value: '' },
        ...mockFilterOptions.subjects.map(s => ({ label: s, value: s })),
      ],
      gradeOptions: [
        { label: '全部年级', value: '' },
        ...mockFilterOptions.grades.map(g => ({ label: g, value: g })),
      ],
      regionOptions: [
        { label: '全部地区', value: '' },
        ...mockFilterOptions.regions.map(r => ({ label: r, value: r })),
      ],
    }
  },

  onLoad() {
    this.loadTeachers()
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.page = 1
    this.loadTeachers()
    uni.stopPullDownRefresh()
  },

  // 上拉加载
  onReachBottom() {
    if (this.loadStatus === 'nomore') return
    this.page++
    this.loadTeachers(true)
  },

  methods: {
    /**
     * 加载教师列表
     * 后续替换为 GET /teachers API
     */
    loadTeachers(append = false) {
      if (this.loading) return
      this.loading = true
      this.loadStatus = 'loading'

      // 模拟API延迟
      setTimeout(() => {
        let data = [...mockTeachers]

        // 关键词搜索
        if (this.keyword) {
          const kw = this.keyword.toLowerCase()
          data = data.filter(t =>
            t.nickname.includes(kw) ||
            t.subjects.some(s => s.includes(kw)) ||
            t.major.includes(kw)
          )
        }

        // 科目筛选
        if (this.filters.subject) {
          data = data.filter(t =>
            t.subjects.some(s => s.includes(this.filters.subject))
          )
        }

        // 年级筛选
        if (this.filters.grade) {
          data = data.filter(t =>
            t.subjects.some(s => s.includes(this.filters.grade))
          )
        }

        // 地区筛选
        if (this.filters.region) {
          data = data.filter(t =>
            t.teaching_regions.includes(this.filters.region)
          )
        }

        // 分页
        const start = (this.page - 1) * this.pageSize
        const pageData = data.slice(start, start + this.pageSize)

        if (append) {
          this.teacherList = [...this.teacherList, ...pageData]
        } else {
          this.teacherList = pageData
        }

        // 判断是否还有更多
        this.loadStatus = (start + this.pageSize >= data.length) ? 'nomore' : 'loadmore'
        this.loading = false
      }, 300)
    },

    /**
     * 搜索
     */
    onSearch() {
      this.page = 1
      this.loadTeachers()
    },

    /**
     * 清除搜索
     */
    onClear() {
      this.keyword = ''
      this.page = 1
      this.loadTeachers()
    },

    /**
     * 筛选条件变更
     */
    onFilterChange() {
      this.page = 1
      this.loadTeachers()
    },

    /**
     * 跳转教师详情
     */
    goToDetail(teacherId) {
      uni.navigateTo({
        url: `/pages/teacher/detail?id=${teacherId}`,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: #F5F5F5;
}

.search-wrapper {
  padding: 10px 12px;
  background: #FFFFFF;
}

.filter-bar {
  background: #FFFFFF;
  border-bottom: 1px solid #F0F0F0;
  margin-bottom: 8px;
}

.teacher-list {
  padding: 0 12px;
}

.teacher-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 12px;
  transition: transform 0.15s;

  &:active {
    transform: translateY(-1px);
  }

  .teacher-avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;

    .avatar-text {
      font-size: 22px;
      font-weight: 700;
      color: #FFFFFF;
    }
  }

  .teacher-info {
    flex: 1;
    min-width: 0;

    .info-name-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 4px;

      .info-name {
        font-size: 16px;
        font-weight: 600;
        color: #1A1A1A;
      }

      .info-rating {
        font-size: 12px;
        color: #FF9500;

        .rating-value {
          margin-left: 2px;
          font-weight: 600;
        }

        .rating-count {
          color: #999999;
          margin-left: 2px;
        }
      }
    }

    .info-school {
      font-size: 12px;
      color: #666666;
      margin-bottom: 6px;
    }

    .info-tags {
      display: flex;
      gap: 6px;
      margin-bottom: 6px;
      flex-wrap: wrap;

      .subject-tag {
        margin: 0;
      }
    }

    .info-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .info-price {
        .price-value {
          font-size: 14px;
          font-weight: 600;
          color: #EE0A24;
        }

        .price-unit {
          font-size: 10px;
          color: #999999;
        }
      }

      .info-region {
        .region-text {
          font-size: 12px;
          color: #999999;
        }
      }
    }
  }
}
</style>
