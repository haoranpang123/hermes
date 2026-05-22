<template>
  <!-- 教师入驻申请页 -->
  <view class="apply-page">
    <view class="apply-header">
      <text class="header-title">👨‍🏫 教师入驻申请</text>
      <text class="header-desc">填写以下信息，提交后等待平台审核</text>
    </view>

    <!-- 表单 -->
    <view class="form-section">
      <!-- 真实姓名 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">真实姓名</text>
          <text class="label-required">*</text>
        </view>
        <u-input
          v-model="form.real_name"
          placeholder="请输入真实姓名"
          border="surround"
          clearable
        />
      </view>

      <!-- 性别 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">性别</text>
          <text class="label-required">*</text>
        </view>
        <u-radio-group v-model="form.gender" placement="row">
          <u-radio
            v-for="item in genderOptions"
            :key="item.value"
            :label="item.label"
            :name="item.value"
            :customStyle="{ marginRight: '24px' }"
          />
        </u-radio-group>
      </view>

      <!-- 学校 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">学校</text>
          <text class="label-required">*</text>
        </view>
        <u-input
          v-model="form.university"
          placeholder="请输入学校名称"
          border="surround"
          clearable
        />
      </view>

      <!-- 专业 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">专业</text>
          <text class="label-required">*</text>
        </view>
        <u-input
          v-model="form.major"
          placeholder="请输入专业名称"
          border="surround"
          clearable
        />
      </view>

      <!-- 年级 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">年级</text>
          <text class="label-required">*</text>
        </view>
        <view class="select-wrapper">
          <view
            v-for="item in gradeOptions"
            :key="item.value"
            class="select-tag"
            :class="{ active: form.grade === item.value }"
            @click="form.grade = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 教学科目（多选） -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">教学科目（最多选5个）</text>
          <text class="label-required">*</text>
        </view>
        <view class="select-wrapper">
          <view
            v-for="item in subjectOptions"
            :key="item.value"
            class="select-tag"
            :class="{
              active: form.subjects.includes(item.value),
              disabled: !form.subjects.includes(item.value) && form.subjects.length >= 5,
            }"
            @click="toggleSubject(item.value)"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 教学年级（多选） -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">可教授年级</text>
          <text class="label-required">*</text>
        </view>
        <view class="select-wrapper">
          <view
            v-for="item in teachingGradeOptions"
            :key="item.value"
            class="select-tag"
            :class="{ active: form.teaching_grades.includes(item.value) }"
            @click="toggleTeachingGrade(item.value)"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 课时费 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">课时费（元/小时）</text>
          <text class="label-required">*</text>
        </view>
        <u-input
          v-model="form.min_price"
          placeholder="请输入课时费"
          type="number"
          border="surround"
          clearable
        >
          <template slot="suffix">
            <text class="input-suffix">元/小时</text>
          </template>
        </u-input>
      </view>

      <!-- 可授课区域（多选） -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">可授课区域</text>
          <text class="label-required">*</text>
        </view>
        <view class="select-wrapper">
          <view
            v-for="item in regionOptions"
            :key="item.value"
            class="select-tag"
            :class="{ active: form.teaching_regions.includes(item.value) }"
            @click="toggleRegion(item.value)"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 个人简介 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">个人简介</text>
          <text class="label-required">*</text>
        </view>
        <u-input
          v-model="form.bio"
          placeholder="请介绍您的教学经验和风格（200字以内）"
          type="textarea"
          border="surround"
          maxlength="200"
          :auto-height="true"
          :height="100"
        />
        <text class="char-count">{{ form.bio.length }}/200</text>
      </view>

      <!-- 学生证上传 -->
      <view class="form-item">
        <view class="form-label">
          <text class="label-text">学生证照片</text>
          <text class="label-required">*</text>
        </view>
        <view class="upload-hint">请上传清晰的学生证照片，最多3张</view>
        <u-upload
          :fileList="certFiles"
          @afterRead="afterRead"
          @delete="deleteFile"
          name="cert"
          multiple
          :maxCount="3"
          :previewFullImage="true"
        />
      </view>
    </view>

    <!-- 提交按钮 -->
    <view class="submit-wrapper">
      <u-button
        type="primary"
        shape="circle"
        size="large"
        :loading="submitting"
        @click="handleSubmit"
      >
        提交申请
      </u-button>
      <text class="submit-desc">提交后将在1-3个工作日内审核</text>
    </view>

    <!-- 提交成功提示 -->
    <u-modal
      v-model="showSuccess"
      title="提交成功"
      content="您的入驻申请已提交，请耐心等待审核。审核通过后即可开始接单。"
      confirm-text="查看审核状态"
      cancel-text="返回"
      @confirm="goToStatus"
      @cancel="goBack"
    />
  </view>
</template>

<script>
import { applyOptions } from '@/common/mock.js'

export default {
  data() {
    return {
      form: {
        real_name: '',
        gender: 'male',
        university: '河南大学',
        major: '',
        grade: '',
        subjects: [],
        teaching_grades: [],
        min_price: '',
        teaching_regions: [],
        bio: '',
      },
      genderOptions: applyOptions.genders,
      gradeOptions: applyOptions.grades,
      subjectOptions: applyOptions.allSubjects,
      teachingGradeOptions: applyOptions.teachingGrades,
      regionOptions: applyOptions.regions,
      certFiles: [],
      submitting: false,
      showSuccess: false,
    }
  },

  methods: {
    /**
     * 切换教学科目
     */
    toggleSubject(value) {
      const idx = this.form.subjects.indexOf(value)
      if (idx > -1) {
        this.form.subjects.splice(idx, 1)
      } else if (this.form.subjects.length < 5) {
        this.form.subjects.push(value)
      }
    },

    /**
     * 切换教学年级
     */
    toggleTeachingGrade(value) {
      const idx = this.form.teaching_grades.indexOf(value)
      if (idx > -1) {
        this.form.teaching_grades.splice(idx, 1)
      } else {
        this.form.teaching_grades.push(value)
      }
    },

    /**
     * 切换区域
     */
    toggleRegion(value) {
      const idx = this.form.teaching_regions.indexOf(value)
      if (idx > -1) {
        this.form.teaching_regions.splice(idx, 1)
      } else {
        this.form.teaching_regions.push(value)
      }
    },

    /**
     * 上传文件后
     */
    afterRead(event) {
      // 模拟上传成功
      const files = Array.isArray(event.file) ? event.file : [event.file]
      files.forEach(f => {
        this.certFiles.push({
          url: f.url || f.path,
          name: f.name || 'cert.jpg',
        })
      })
    },

    /**
     * 删除文件
     */
    deleteFile(event) {
      this.certFiles.splice(event.index, 1)
    },

    /**
     * 提交申请
     */
    handleSubmit() {
      // 表单校验
      if (!this.form.real_name) {
        uni.showToast({ title: '请填写真实姓名', icon: 'none' })
        return
      }
      if (!this.form.major) {
        uni.showToast({ title: '请填写专业', icon: 'none' })
        return
      }
      if (!this.form.grade) {
        uni.showToast({ title: '请选择年级', icon: 'none' })
        return
      }
      if (this.form.subjects.length === 0) {
        uni.showToast({ title: '请选择教学科目', icon: 'none' })
        return
      }
      if (this.form.teaching_grades.length === 0) {
        uni.showToast({ title: '请选择可教授年级', icon: 'none' })
        return
      }
      if (!this.form.min_price || parseInt(this.form.min_price) <= 0) {
        uni.showToast({ title: '请填写有效的课时费', icon: 'none' })
        return
      }
      if (this.form.teaching_regions.length === 0) {
        uni.showToast({ title: '请选择可授课区域', icon: 'none' })
        return
      }
      if (!this.form.bio) {
        uni.showToast({ title: '请填写个人简介', icon: 'none' })
        return
      }
      if (this.certFiles.length === 0) {
        uni.showToast({ title: '请上传学生证照片', icon: 'none' })
        return
      }

      this.submitting = true
      // 模拟提交
      setTimeout(() => {
        this.submitting = false
        this.showSuccess = true
        // 保存审核状态
        uni.setStorageSync('teacherAuditStatus', 'pending')
      }, 1000)
    },

    /**
     * 查看审核状态
     */
    goToStatus() {
      this.showSuccess = false
      uni.redirectTo({ url: '/pages/teacher/status' })
    },

    /**
     * 返回
     */
    goBack() {
      this.showSuccess = false
      uni.navigateBack()
    },
  },
}
</script>

<style lang="scss" scoped>
.apply-page {
  background: #F5F5F5;
  min-height: 100vh;
  padding-bottom: 40px;
}

.apply-header {
  background: linear-gradient(135deg, #07C160, #06AD56);
  padding: 20px;
  color: #FFFFFF;
  text-align: center;

  .header-title {
    font-size: 18px;
    font-weight: 700;
    display: block;
  }

  .header-desc {
    font-size: 13px;
    opacity: 0.85;
    margin-top: 4px;
    display: block;
  }
}

.form-section {
  padding: 12px;
}

.form-item {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);

  .form-label {
    margin-bottom: 10px;

    .label-text {
      font-size: 14px;
      font-weight: 600;
      color: #1A1A1A;
    }

    .label-required {
      color: #EE0A24;
      margin-left: 4px;
      font-size: 14px;
    }
  }

  .input-suffix {
    font-size: 12px;
    color: #999999;
    margin-right: 4px;
  }

  .char-count {
    font-size: 12px;
    color: #999999;
    text-align: right;
    margin-top: 4px;
    display: block;
  }
}

.select-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .select-tag {
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 13px;
    border: 1px solid #EBEDF0;
    color: #666666;
    background: #FFFFFF;
    transition: all 0.2s;

    &.active {
      background: #E8F8EF;
      color: #07C160;
      border-color: #07C160;
      font-weight: 600;
    }

    &.disabled {
      opacity: 0.4;
    }
  }
}

.upload-hint {
  font-size: 12px;
  color: #999999;
  margin-bottom: 8px;
}

.submit-wrapper {
  padding: 16px 12px;
  text-align: center;

  .submit-desc {
    font-size: 12px;
    color: #999999;
    margin-top: 8px;
    display: block;
  }
}
</style>
