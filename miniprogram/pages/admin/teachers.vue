<template>
  <!-- 管理后台 — 教师审核页：Tab切换 + 教师卡片列表 -->
  <view class="admin-teachers-page">
    <!-- Tab 切换 -->
    <u-tabs
      :list="tabs"
      :current="currentTab"
      @change="onTabChange"
      :activeStyle="{ color: '#07C160' }"
      lineColor="#07C160"
    />

    <!-- 教师列表 -->
    <view class="teacher-content">
      <view
        v-for="teacher in teachers"
        :key="teacher.teacher_id"
        class="teacher-card"
      >
        <!-- 卡片主体 -->
        <view class="card-body">
          <view
            class="teacher-avatar"
            :style="{ background: teacher._avatarBg || '#1989FA' }"
          >
            <text class="avatar-text">{{ teacher._initial || '师' }}</text>
          </view>
          <view class="teacher-info">
            <view class="info-row">
              <text class="teacher-name">{{ teacher.real_name }}</text>
              <text class="teacher-gender">{{ teacher.gender === 'male' ? '男' : teacher.gender === 'female' ? '女' : '' }}</text>
            </view>
            <text class="teacher-school">{{ teacher.university }}{{ teacher.major ? ' · ' + teacher.major : '' }}</text>
            <text class="teacher-grade">{{ teacher.grade }}</text>
            <text class="teacher-phone">电话：{{ teacher.phone }}</text>
            <text class="teacher-time">申请时间：{{ formatDate(teacher.created_at) }}</text>
          </view>
        </view>

        <!-- 待审核：操作按钮 -->
        <view v-if="currentTab === 0" class="card-actions">
          <view class="btn-approve" @click.stop="onApprove(teacher)">
            <text>通过</text>
          </view>
          <view class="btn-reject" @click.stop="onReject(teacher)">
            <text>拒绝</text>
          </view>
        </view>

        <!-- 已通过：状态标签 -->
        <view v-if="currentTab === 1" class="card-status">
          <text class="badge-approved">已通过</text>
        </view>

        <!-- 已拒绝：状态标签 + 拒绝原因 -->
        <view v-if="currentTab === 2" class="card-status">
          <text class="badge-rejected">已拒绝</text>
          <text v-if="teacher.reject_reason" class="reject-reason">原因：{{ teacher.reject_reason }}</text>
        </view>
      </view>

      <!-- 空状态 -->
      <u-empty
        v-if="!loading && teachers.length === 0"
        text="暂无数据"
        mode="list"
        margin-top="80"
      />
    </view>
  </view>
</template>

<script>
import { getPaginated, postData } from '@/utils/api.js'

const COLOR_PALETTE = [
  '#1989FA', '#07C160', '#FF976A', '#EE0A24',
  '#9C27B0', '#FF9800', '#607D8B', '#E91E63',
]

export default {
  data() {
    return {
      tabs: [
        { name: '待审核', value: 'pending' },
        { name: '已通过', value: 'approved' },
        { name: '已拒绝', value: 'rejected' },
      ],
      currentTab: 0,
      teachers: [],
      loading: false,
      page: 1,
      pageSize: 20,
      total: 0,
      hasMore: true,
    }
  },

  onLoad() {
    this.fetchTeachers()
  },

  onShow() {
    this.page = 1
    this.hasMore = true
    this.fetchTeachers()
  },

  onPullDownRefresh() {
    this.page = 1
    this.hasMore = true
    this.fetchTeachers().finally(() => {
      uni.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.hasMore && !this.loading) {
      this.page++
      this.fetchTeachers(true)
    }
  },

  methods: {
    /**
     * 获取当前Tab对应的审核状态
     */
    getAuditStatus() {
      return this.tabs[this.currentTab].value
    },

    /**
     * 拉取教师审核列表
     */
    async fetchTeachers(append = false) {
      this.loading = true
      try {
        const params = {
          audit_status: this.getAuditStatus(),
          page: this.page,
          page_size: this.pageSize,
        }

        const result = await getPaginated('/api/v1/admin/teachers', params, { showLoading: !append })

        // 为每条数据生成首字母及随机颜色
        const items = (result.items || []).map((item) => ({
          ...item,
          _initial: (item.real_name && item.real_name[0]) || '师',
          _avatarBg: COLOR_PALETTE[(item.teacher_id || 0) % COLOR_PALETTE.length],
        }))

        if (append) {
          this.teachers = [...this.teachers, ...items]
        } else {
          this.teachers = items
        }
        this.total = result.total
        this.hasMore = this.teachers.length < this.total
      } catch (err) {
        if (!append) {
          this.teachers = []
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
      this.fetchTeachers()
    },

    /**
     * 格式化日期
     */
    formatDate(dateStr) {
      if (!dateStr) return ''
      return dateStr.substring(0, 10)
    },

    /**
     * 审核通过
     */
    async onApprove(teacher) {
      try {
        await postData(`/api/v1/admin/teachers/${teacher.teacher_id}/approve`)
        uni.showToast({ title: '审核通过', icon: 'success' })
        this.page = 1
        this.hasMore = true
        this.fetchTeachers()
      } catch (err) {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    },

    /**
     * 审核拒绝
     */
    onReject(teacher) {
      uni.showModal({
        title: '拒绝原因',
        editable: true,
        placeholderText: '请输入拒绝原因（选填）',
        success: async (res) => {
          if (res.confirm) {
            try {
              await postData(`/api/v1/admin/teachers/${teacher.teacher_id}/reject`, {
                reason: res.content || '',
              })
              uni.showToast({ title: '已驳回', icon: 'success' })
              this.page = 1
              this.hasMore = true
              this.fetchTeachers()
            } catch (err) {
              uni.showToast({ title: err.message || '操作失败', icon: 'none' })
            }
          }
        },
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.admin-teachers-page {
  background: #F5F5F5;
  min-height: 100vh;
}

.teacher-content {
  padding: 10px 12px;
}

.teacher-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .card-body {
    display: flex;
    gap: 10px;

    .teacher-avatar {
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

    .teacher-info {
      flex: 1;

      .info-row {
        display: flex;
        align-items: center;
        gap: 6px;

        .teacher-name {
          font-size: 14px;
          font-weight: 600;
          color: #1A1A1A;
        }

        .teacher-gender {
          font-size: 11px;
          color: #666666;
        }
      }

      .teacher-school {
        font-size: 12px;
        color: #666666;
        display: block;
        margin: 2px 0;
      }

      .teacher-grade {
        font-size: 12px;
        color: #666666;
        display: block;
      }

      .teacher-phone {
        font-size: 12px;
        color: #999999;
        display: block;
        margin-top: 2px;
      }

      .teacher-time {
        font-size: 12px;
        color: #999999;
        display: block;
      }
    }
  }

  // 待审核：操作按钮
  .card-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid #F0F0F0;

    .btn-approve {
      padding: 6px 18px;
      border-radius: 16px;
      background: #07C160;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 500;
    }

    .btn-reject {
      padding: 6px 18px;
      border-radius: 16px;
      background: #EE0A24;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 500;
    }
  }

  // 已通过/已拒绝：状态标签
  .card-status {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #F0F0F0;

    .badge-approved {
      font-size: 12px;
      font-weight: 500;
      color: #07C160;
      padding: 2px 10px;
      background: rgba(7, 193, 96, 0.08);
      border-radius: 4px;
    }

    .badge-rejected {
      font-size: 12px;
      font-weight: 500;
      color: #EE0A24;
      padding: 2px 10px;
      background: rgba(238, 10, 36, 0.08);
      border-radius: 4px;
    }

    .reject-reason {
      font-size: 11px;
      color: #999999;
      flex: 1;
    }
  }
}
</style>
