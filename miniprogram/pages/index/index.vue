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
import { getPaginated } from '@/utils/api.js'

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
      totalPages: 1,
      loading: false,
      loadStatus: 'loadmore', // loadmore | loading | nomore

      // 筛选选项（从后端动态加载，保留常用备选）
      subjectOptions: [
        { label: '全部科目', value: '' },
        { label: '数学', value: '数学' },
        { label: '英语', value: '英语' },
        { label: '物理', value: '物理' },
        { label: '化学', value: '化学' },
        { label: '语文', value: '语文' },
      ],
      gradeOptions: [
        { label: '全部年级', value: '' },
        { label: '小学', value: '小学' },
        { label: '初中', value: '初中' },
        { label: '高中', value: '高中' },
      ],
      regionOptions: [
        { label: '全部地区', value: '' },
        { label: '龙亭区', value: '龙亭区' },
        { label: '顺河区', value: '顺河区' },
        { label: '鼓楼区', value: '鼓楼区' },
        { label: '禹王台区', value: '禹王台区' },
        { label: '金明区', value: '金明区' },
      ],
    }
  },

  onLoad() {
    this.loadTeachers()
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.page = 1
    this.loadTeachers().finally(() => {
      uni.stopPullDownRefresh()
    })
  },

  // 上拉加载
  onReachBottom() {
    if (this.loadStatus === 'nomore' || this.loading) return
    if (this.page >= this.totalPages) return
    this.page++
    this.loadTeachers(true)
  },

  methods: {
    /**
     * 加载教师列表 — 调用 GET /api/v1/teachers
     */
    async loadTeachers(append = false) {
      if (this.loading) return
      this.loading = true
      this.loadStatus = 'loading'

      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
        }
        if (this.keyword) params.keyword = this.keyword
        if (this.filters.subject) params.subjects = this.filters.subject
        if (this.filters.grade) params.grade_level = this.filters.grade
        if (this.filters.region) params.region = this.filters.region

        const result = await getPaginated('/api/v1/teachers', params)

        // 将后端字段映射到模板字段
        const items = result.items.map(mapTeacherItem)

        if (append) {
          this.teacherList = [...this.teacherList, ...items]
        } else {
          this.teacherList = items
        }

        this.totalPages = result.total_pages || 1
        this.loadStatus = (this.page >= this.totalPages) ? 'nomore' : 'loadmore'
      } catch (e) {
        console.error('加载教师列表失败:', e)
        this.loadStatus = 'loadmore'
      } finally {
        this.loading = false
      }
    },

    /** 搜索 */
    onSearch() {
      this.page = 1
      this.loadTeachers()
    },

    /** 清除搜索 */
    onClear() {
      this.keyword = ''
      this.page = 1
      this.loadTeachers()
    },

    /** 筛选条件变更 */
    onFilterChange() {
      this.page = 1
      this.loadTeachers()
    },

    /** 跳转教师详情 */
    goToDetail(teacherId) {
      uni.navigateTo({
        url: `/pages/teacher/detail?id=${teacherId}`,
      })
    },
  },
}

/**
 * 将后端教师列表项映射为模板需要的字段
 */
function mapTeacherItem(item) {
  const subjects = item.subjects || []
  const regions = item.teaching_regions || []
  const name = item.nickname || ''
  return {
    teacher_id: item.teacher_id,
    nickname: name,
    avatar_url: item.avatar_url || '',
    avatar_bg: item.avatar_bg || randomAvatarBg(item.teacher_id),
    initial: name ? name[0] : '?',
    university: item.university || '',
    major: item.major || '',
    grade: item.grade || '',
    subjects: subjects.map(s => (typeof s === 'string' ? s : s.subject || s)),
    min_price: item.min_price || 0,
    avg_rating: item.avg_rating ? parseFloat(item.avg_rating).toFixed(1) : '0.0',
    review_count: item.review_count || 0,
    is_available: item.is_available,
    teaching_regions: regions,
    gender: item.gender || '',
    bio: item.bio || '',
  }
}

/** 根据 teacher_id 生成一个随机渐变色 */
function randomAvatarBg(id) {
  const colors = [
    'linear-gradient(135deg, #FF6B6B, #EE5A24)',
    'linear-gradient(135deg, #4ECDC4, #44BD32)',
    'linear-gradient(135deg, #A29BFE, #6C5CE7)',
    'linear-gradient(135deg, #FDCB6E, #F39C12)',
    'linear-gradient(135deg, #55E7FC, #0093E9)',
    'linear-gradient(135deg, #FD79A8, #E84393)',
  ]
  return colors[(id || 1) % colors.length]
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
