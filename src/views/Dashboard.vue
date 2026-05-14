<template>
  <div class="dashboard-content">
    <div class="info-cards">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card>
            <div class="card-content">
              <div class="card-info">
                <span>今日学习时长</span>
                <span>{{ overview.stats.studyHoursToday }}<span style="font-size: 16px;">h</span></span>
              </div>
              <div>
                <el-icon style="color:#024ae2"><Clock /></el-icon>
              </div>
            </div>
            <div class="card-footer">
              <div>较昨日 {{ formatChange(overview.changes.studyHoursToday) }}</div>
            </div>          
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card>
            <div class="card-content">
              <div class="card-info">
                <span>待复习</span>
                <span>{{ overview.stats.reviewTodoCount }}</span>
              </div>
              <div>
                <el-icon style="color:#12778d"><Collection /></el-icon>
              </div>
            </div>
            <div class="card-footer">
              <div>较昨日 {{ formatChange(overview.changes.reviewTodoCount) }}</div>
            </div>          
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card>
            <div class="card-content">
              <div class="card-info">
                <span>刷题数量</span>
                <span>{{ overview.stats.algorithmSolvedCount }}</span>
              </div>
              <div>
                <el-icon style="color:#1E6CEF"><Finished /></el-icon>
              </div>
            </div>
            <div class="card-footer">
              <div>较昨日 {{ formatChange(overview.changes.algorithmSolvedCount) }}</div>
            </div>          
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card>
            <div class="card-content">
              <div class="card-info">
                <span>投递数量</span>
                <span>{{ overview.stats.applicationCount }}</span>
              </div>
              <div>
                <el-icon style="color:#0D75EA"><Promotion /></el-icon>
              </div>
            </div>
            <div class="card-footer">
              <div>较昨日 {{ formatChange(overview.changes.applicationCount) }}</div>
            </div>          
          </el-card>
        </el-col>
        <el-col :span="5">
          <el-card>
            <div class="card-content">
              <div class="card-info">
                <span>模拟面试</span>
                <span>{{ overview.stats.mockInterviewCount }}</span>
              </div>
              <div>
                <el-icon style="color:#F58530"><User /></el-icon>
              </div>
            </div>
            <div class="card-footer">
              <div>较昨日 {{ formatChange(overview.changes.mockInterviewCount) }}</div>
            </div>          
          </el-card>
        </el-col>
      </el-row>
    </div>
    <div class="middle-cards">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <div class="middle-header">
              <div>今日学习计划</div>
            </div>
            <div class="plan-list">
              <div
                v-for="plan in todayPlans"
                :key="plan.id"
                class="plan-item"
                :class="{ active: plan.completed }"
              >
                <div class="check-box" @click="togglePlan(plan)">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="plan-title">
                  <span>{{ plan.title }}</span>
                  <span class="tag" :class="planTypeClass(plan.type)">{{ displayPlanType(plan.type) }}</span>
                </div>
                <div class="plan-time">{{ formatPlanTime(plan) }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="panel-card">
            <div class="middle-header">
              <div>知识点掌握度</div>
            </div>
            <div class="mastery-content">
              <div class="donut-chart">
                <div class="donut-center">
                  <span>{{ overview.mastery.overall }}%</span>
                  <span>总体掌握度</span>
                </div>
              </div>
              <div class="legend-list">
                <div class="legend-item">
                  <span class="dot deep"></span>
                  <span>已掌握</span>
                  <strong>32%</strong>
                </div>
                <div class="legend-item">
                  <span class="dot green"></span>
                  <span>较熟悉</span>
                  <strong>36%</strong>
                </div>
                <div class="legend-item">
                  <span class="dot yellow"></span>
                  <span>一般</span>
                  <strong>18%</strong>
                </div>
                <div class="legend-item">
                  <span class="dot red"></span>
                  <span>较弱</span>
                  <strong>10%</strong>
                </div>
                <div class="legend-item">
                  <span class="dot gray"></span>
                  <span>未掌握</span>
                  <strong>4%</strong>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="panel-card">
            <div class="middle-header">
              <div>薄弱知识点 Top5</div>
              <div class="more-link">更多 <el-icon><ArrowRight /></el-icon></div>
            </div>
            <div class="weak-list">
              <div class="weak-item" v-for="point in overview.weakPoints" :key="point.name">
                <div class="weak-title">
                  <span>{{ point.name }}</span>
                  <span>{{ point.mastery }}%</span>
                </div>
                <div class="weak-progress" :class="{ orange: point.mastery >= 50, yellow: point.mastery >= 60 }">
                  <span :style="{ width: `${point.mastery}%` }"></span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <div class="bottom-cards">
      <el-row :gutter="20">
        <el-col :span="13">
          <el-card class="panel-card interview-card">
            <div class="middle-header">
              <div>最近面试记录</div>
              <div class="more-link">更多 <el-icon><ArrowRight /></el-icon></div>
            </div>
            <div class="interview-table">
              <div class="table-row table-head">
                <div>公司</div>
                <div>岗位</div>
                <div>时间</div>
                <div>结果</div>
                <div>操作</div>
              </div>
              <div class="table-row" v-for="record in recentExperiences" :key="record.id">
                <div class="company">
                  <span class="logo" :class="logoClass(record.company)">{{ logoText(record.company) }}</span>
                  <span>{{ record.company }}</span>
                </div>
                <div>{{ record.role }}</div>
                <div>{{ record.date }}</div>
                <div><span class="result" :class="roundClass(record.round)">{{ record.round }}</span></div>
                <div class="table-actions">
                  <el-icon><Document /></el-icon>
                  <el-icon><Delete /></el-icon>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="11">
          <el-card class="panel-card quick-card">
            <div class="middle-header">
              <div>快捷操作</div>
            </div>
            <div class="quick-grid">
              <div class="quick-item">
                <el-icon class="blue"><Finished /></el-icon>
                <span>刷算法题</span>
              </div>
              <div class="quick-item">
                <el-icon class="blue"><Notebook /></el-icon>
                <span>新建笔记</span>
              </div>
              <div class="quick-item">
                <el-icon class="blue"><Promotion /></el-icon>
                <span>投递内推</span>
              </div>
              <div class="quick-item">
                <el-icon class="orange"><User /></el-icon>
                <span>模拟面试</span>
              </div>
              <div class="quick-item">
                <el-icon class="green"><Reading /></el-icon>
                <span>知识点学习</span>
              </div>
              <div class="quick-item">
                <el-icon class="red"><Close /></el-icon>
                <span>错题本</span>
              </div>
              <div class="quick-item">
                <el-icon class="blue"><Tickets /></el-icon>
                <span>面经收集</span>
              </div>
              <div class="quick-item">
                <el-icon class="blue"><Calendar /></el-icon>
                <span>学习计划</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>

</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { dashboardApi, experienceApi } from '@/api/front'

const overview = reactive({
  stats: {
    studyHoursToday: 2.6,
    reviewTodoCount: 12,
    algorithmSolvedCount: 48,
    applicationCount: 8,
    mockInterviewCount: 2
  },
  changes: {
    studyHoursToday: -3,
    reviewTodoCount: -3,
    algorithmSolvedCount: 16,
    applicationCount: 2,
    mockInterviewCount: 1
  },
  mastery: {
    overall: 68
  },
  weakPoints: [
    { name: 'Vue3 响应式原理', mastery: 40 },
    { name: '虚拟 DOM', mastery: 45 },
    { name: '组件通信', mastery: 50 },
    { name: 'TypeScript 泛型', mastery: 60 },
    { name: '工程化构建', mastery: 65 }
  ]
})

const todayPlans = reactive([
  { id: 'plan_001', title: 'Vue3 响应式原理', type: '知识点', startTime: '09:00', endTime: '10:00', completed: true },
  { id: 'plan_002', title: 'LeetCode 题目练习', type: '算法', startTime: '10:30', endTime: '12:00', completed: false },
  { id: 'plan_003', title: '项目：仿掘金首页', type: '项目', startTime: '14:00', endTime: '16:00', completed: false },
  { id: 'plan_004', title: '模板面试：Vue 生态', type: '模拟面试', startTime: '16:30', endTime: '17:30', completed: false },
  { id: 'plan_005', title: '总结回顾', type: '复盘', startTime: '20:00', endTime: '20:30', completed: false }
])

const recentExperiences = reactive([
  { id: 'exp_001', company: '字节跳动', role: '前端开发实习生', date: '2026-04-18', round: '一面' },
  { id: 'exp_002', company: '阿里巴巴', role: '前端开发实习生', date: '2026-04-24', round: '二面' },
  { id: 'exp_003', company: '腾讯', role: '前端开发实习生', date: '2026-05-02', round: 'HR 面' }
])

function formatChange(value = 0) {
  return value > 0 ? `+${value}` : String(value)
}

function formatClock(value) {
  if (!value) return '--:--'
  const date = new Date(value)
  if (!Number.isNaN(date.getTime())) {
    return date.toTimeString().slice(0, 5)
  }
  return String(value).slice(0, 5)
}

function formatPlanTime(plan) {
  return `${formatClock(plan.startTime)} - ${formatClock(plan.endTime)}`
}

function planTypeClass(type = '') {
  if (type.includes('算法') || type.includes('面试')) return 'orange'
  if (type.includes('项目')) return 'blue'
  if (type.includes('复盘')) return 'gray'
  return 'green'
}

function displayPlanType(type = '') {
  return type.length > 6 ? `${type.slice(0, 6)}...` : type
}

function logoText(company = '') {
  return company.length > 2 ? company.slice(0, 1) : ''
}

function logoClass(company = '') {
  if (company.includes('字节')) return 'bytedance'
  if (company.includes('阿里')) return 'alibaba'
  if (company.includes('腾讯')) return 'tencent'
  return ''
}

function roundClass(round = '') {
  if (round.includes('HR') || round.includes('挂') || round.includes('结束')) return 'red'
  if (round.includes('二')) return 'orange'
  return 'blue'
}

async function loadOverview() {
  const data = await dashboardApi.getOverview()
  Object.assign(overview.stats, data.stats || {})
  Object.assign(overview.changes, data.changes || {})
  Object.assign(overview.mastery, data.mastery || {})
  if (Array.isArray(data.weakPoints) && data.weakPoints.length) {
    overview.weakPoints = data.weakPoints
  }
}

async function loadTodayPlans() {
  const data = await dashboardApi.getTodayPlan()
  if (Array.isArray(data) && data.length) {
    todayPlans.splice(0, todayPlans.length, ...data)
  }
}

async function togglePlan(plan) {
  const nextCompleted = !plan.completed
  plan.completed = nextCompleted
  try {
    await dashboardApi.updateTodayPlan(plan.id, { completed: nextCompleted })
  } catch {
    plan.completed = !nextCompleted
  }
}

async function loadRecentExperiences() {
  const data = await experienceApi.getList({ page: 1, pageSize: 3 })
  const list = data.list || data
  if (Array.isArray(list) && list.length) {
    recentExperiences.splice(0, recentExperiences.length, ...list.slice(0, 3))
  }
}

onMounted(async () => {
  await Promise.allSettled([loadOverview(), loadTodayPlans(), loadRecentExperiences()])
})
</script>


<style lang="scss" scoped>
.dashboard-content {
  text-align: left;
  color: #1f2937;

  :deep(.el-card) {
    border: 1px solid #e1e6ef;
    border-radius: 8px;
    box-shadow: none;
  }

  :deep(.el-card__body) {
    padding: 22px 24px;
  }

  .info-cards {
    margin-bottom: 20px;

    .card-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 100px;

      .card-info {
        display: flex;
        flex-direction: column;
        gap: 5px;
        justify-content: space-between;

        span:first-child {
          font-size: 16px;
          color: #333;
          font-weight: bold;
          margin-bottom: 20px;
        }

        span:last-child {
          font-size: 40px;
          font-weight: bold;
          color: #000;
        }
      }

      .el-icon {
        font-size: 50px;
      }

    }

    .card-footer {
      margin-top: 10px;
      font-size: 15px;
      color: #999;
    }
  }

  .middle-cards {
    margin-bottom: 20px;

    :deep(.el-row) {
      align-items: stretch;
    }

    :deep(.el-col) {
      display: flex;
    }

    :deep(.el-card) {
      width: 100%;
      height: 100%;
      min-height: 330px;
      background-color: #f9fafb;
    }

    :deep(.el-card__body) {
      height: 100%;
      box-sizing: border-box;
    }
  }

  .panel-card {
    min-height: 300px;
  }

  .middle-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
    font-size: 18px;
    font-weight: 700;
    color: #111827;
  }

  .add-task,
  .more-link {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 600;
    color: #0d6efd;
  }

  .more-link {
    color: #f04438;
  }

  .plan-list {
    display: flex;
    flex-direction: column;
    gap: 19px;
  }

  .plan-item {
    position: relative;
    display: grid;
    grid-template-columns: 22px minmax(0, 1fr) 96px;
    align-items: center;
    gap: 14px;
    min-height: 28px;

    &::before {
      content: '';
      position: absolute;
      left: 10px;
      top: 25px;
      width: 1px;
      height: 22px;
      border-left: 1px dashed #d8dee8;
    }

    &:last-child::before {
      display: none;
    }

    .check-box {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 18px;
      height: 18px;
      border: 2px solid #cbd5e1;
      border-radius: 4px;
      color: #fff;
      font-size: 13px;
      box-sizing: border-box;
      background-color: #fff;
    }

    &.active .check-box {
      border-color: #1e6cef;
      background-color: #1e6cef;
    }

    .plan-title {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      color: #263241;
      font-size: 15px;

      > span:first-child {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .plan-time {
      color: #697386;
      font-size: 14px;
      text-align: right;
      white-space: nowrap;
    }
  }

  .tag {
    flex: 0 0 auto;
    max-width: 88px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 13px;
    line-height: 18px;

    &.green {
      color: #079455;
      background-color: #dcfae6;
      border: 1px solid #a9efc5;
    }

    &.orange {
      color: #f97316;
      background-color: #fff1e5;
      border: 1px solid #fed7aa;
    }

    &.blue {
      color: #1e6cef;
      background-color: #e8f1ff;
      border: 1px solid #bfd8ff;
    }

    &.gray {
      color: #667085;
      background-color: #f2f4f7;
      border: 1px solid #d0d5dd;
    }
  }

  .mastery-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    min-height: 220px;
  }

  .donut-chart {
    position: relative;
    width: 170px;
    height: 170px;
    border-radius: 50%;
    background:
      conic-gradient(
        #37c6ad 0deg 116deg,
        #2f8df5 116deg 246deg,
        #ffb020 246deg 311deg,
        #f04438 311deg 347deg,
        #d0d5dd 347deg 360deg
      );

    &::before {
      content: '';
      position: absolute;
      inset: 22px;
      border-radius: 50%;
      background-color: #fff;
    }
  }

  .donut-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #111827;

    span:first-child {
      font-size: 28px;
      font-weight: 800;
      line-height: 1.2;
    }

    span:last-child {
      margin-top: 6px;
      color: #667085;
      font-size: 13px;
    }
  }

  .legend-list {
    width: 150px;
  }

  .legend-item {
    display: grid;
    grid-template-columns: 10px 1fr auto;
    align-items: center;
    gap: 10px;
    margin-bottom: 17px;
    color: #344054;
    font-size: 15px;

    strong {
      color: #1d2939;
      font-size: 16px;
    }
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;

    &.deep {
      background-color: #0887a2;
    }

    &.green {
      background-color: #37c6ad;
    }

    &.yellow {
      background-color: #ffb020;
    }

    &.red {
      background-color: #f04438;
    }

    &.gray {
      background-color: #d0d5dd;
    }
  }

  .weak-list {
    display: flex;
    flex-direction: column;
    gap: 22px;
  }

  .weak-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    color: #344054;
    font-size: 14px;

    span:last-child {
      color: #1d2939;
      font-weight: 600;
    }
  }

  .weak-progress {
    height: 5px;
    overflow: hidden;
    border-radius: 999px;
    background-color: #edf1f7;

    span {
      display: block;
      height: 100%;
      border-radius: inherit;
      background-color: #ef4444;
    }

    &.orange span {
      background-color: #f97316;
    }

    &.yellow span {
      background-color: #fbbf24;
    }
  }

  .bottom-cards {
    .panel-card {
      min-height: 250px;
    }
  }

  .interview-table {
    color: #344054;
    font-size: 14px;
  }

  .table-row {
    display: grid;
    grid-template-columns: 1.25fr 1.55fr 1.1fr 0.7fr 0.7fr;
    align-items: center;
    min-height: 52px;
    border-bottom: 1px solid #edf1f7;

    &:last-child {
      border-bottom: none;
    }
  }

  .table-head {
    min-height: 38px;
    color: #667085;
    font-weight: 500;
  }

  .company,
  .table-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .table-actions {
    gap: 18px;
    color: #1f2937;
    font-size: 20px;
  }

  .logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 5px;
    color: #fff;
    font-size: 11px;
    font-weight: 800;

    &.bytedance {
      background: linear-gradient(135deg, #06b6d4, #1e6cef);
    }

    &.alibaba {
      background-color: #ff7a00;
    }

    &.tencent {
      background: linear-gradient(135deg, #1e6cef, #22c55e);
    }
  }

  .result {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 40px;
    padding: 2px 8px;
    border-radius: 5px;
    font-size: 13px;

    &.blue {
      color: #1e6cef;
      background-color: #e8f1ff;
      border: 1px solid #bfd8ff;
    }

    &.orange {
      color: #f97316;
      background-color: #fff1e5;
      border: 1px solid #fed7aa;
    }

    &.red {
      color: #f04438;
      background-color: #fee4e2;
      border: 1px solid #fecdca;
    }
  }

  .quick-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
  }

  .quick-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 82px;
    border: 1px solid #e1e6ef;
    border-radius: 6px;
    color: #111827;
    font-size: 14px;
    font-weight: 600;
    background-color: #fff;

    .el-icon {
      margin-bottom: 10px;
      font-size: 30px;
    }

    .blue {
      color: #1e6cef;
    }

    .orange {
      color: #f97316;
    }

    .green {
      color: #0887a2;
    }

    .red {
      color: #ef4444;
    }
  }
}
</style>
