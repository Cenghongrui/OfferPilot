<template>
  <div class="op-page profile-page">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">个人中心</div>
        <h1 class="op-title">个人中心</h1>
        <p class="op-subtitle">查看你的求职准备档案、学习目标和最近训练概览。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Setting" @click="router.push('/back/settings')">编辑资料</el-button>
      </div>
    </section>

    <section class="profile-grid">
      <el-card class="profile-card" shadow="never">
        <div class="profile-head">
          <div class="avatar">{{ userInitial }}</div>
          <div>
            <h2>{{ auth.user?.name }}</h2>
            <p>{{ auth.user?.email }}</p>
          </div>
        </div>
        <div class="goal-box">
          <span>当前学习目标</span>
          <strong>{{ auth.user?.goal }}</strong>
        </div>
      </el-card>

      <div class="op-grid cols-3 overview">
        <div class="op-stat" v-for="item in overview" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section class="op-card pad">
      <div class="op-section-title">
        <span>最近动态</span>
      </div>
      <div class="activity-list">
        <div v-for="item in activities" :key="item.title" class="activity-item">
          <span :class="item.type"></span>
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore'
import { profileApi } from '@/api/front'

const router = useRouter()
const auth = useAuthStore()
const userInitial = computed(() => auth.user?.name?.slice(0, 1).toUpperCase() || 'U')

const overview = reactive([
  { label: '待复习题目', value: 12 },
  { label: '进行中投递', value: 3 },
  { label: '模拟面试均分', value: 14 }
])

const activities = reactive([
  { type: 'blue', title: '完成 Vue 专项模拟面试', desc: '生成一份复盘报告，建议补充 diff 和 key 的追问。' },
  { type: 'green', title: '投递状态更新', desc: '腾讯前端实习进入一面阶段，下一步准备项目深挖。' },
  { type: 'orange', title: '题库复习提醒', desc: '事件循环和浏览器缓存仍处于待掌握状态。' }
])

onMounted(async () => {
  const data = await profileApi.getOverview()
  if (data.user) auth.syncCurrentUser(data.user)
  if (data.overview) {
    overview.splice(
      0,
      overview.length,
      { label: '待复习题目', value: data.overview.reviewTodoCount },
      { label: '进行中投递', value: data.overview.activeApplicationCount },
      { label: '模拟面试均分', value: data.overview.mockInterviewAverageScore }
    )
  }
  if (Array.isArray(data.activities) && data.activities.length) {
    activities.splice(0, activities.length, ...data.activities)
  }
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.profile-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 8px;
  color: #fff;
  background: #2563eb;
  font-size: 28px;
  font-weight: 800;
}

.profile-head h2 {
  margin: 0;
  color: #172033;
  font-size: 22px;
  font-weight: 800;
}

.profile-head p {
  margin-top: 6px;
  color: #667085;
}

.goal-box {
  margin-top: 24px;
  padding: 14px;
  border-radius: 8px;
  background: #eff6ff;
}

.goal-box span {
  display: block;
  color: #2563eb;
  font-size: 13px;
  font-weight: 800;
}

.goal-box strong {
  display: block;
  margin-top: 8px;
  color: #172033;
  line-height: 1.5;
}

.overview {
  height: 100%;
}

.activity-list {
  display: grid;
  gap: 12px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.activity-item > span {
  width: 10px;
  min-width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 50%;
}

.activity-item .blue {
  background: #2563eb;
}

.activity-item .green {
  background: #16a34a;
}

.activity-item .orange {
  background: #f59e0b;
}

.activity-item strong {
  color: #172033;
}

.activity-item p {
  margin-top: 5px;
  color: #667085;
}

@media (max-width: 1100px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
