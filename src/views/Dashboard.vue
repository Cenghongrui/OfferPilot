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
              <el-empty v-if="todayPlans.length === 0" description="今日待计划，点击下方按钮添加任务" />
              <div
                v-else
                v-for="plan in todayPlans"
                :key="plan.id"
                class="plan-item"
                :class="{ active: plan.completed }"
              >
                <div class="check-box" @click="togglePlan(plan)">
                  <el-icon><Check /></el-icon>
                </div>
                <div class="plan-title">
                  <span
                    v-if="editingPlanId !== plan.id || editingField !== 'title'"
                    @dblclick="startEdit(plan, 'title')"
                    class="editable-text"
                    :title="'双击编辑'"
                  >{{ plan.title }}</span>
                  <el-input
                    v-else
                    v-model="editBuffer"
                    size="small"
                    @blur="commitEdit(plan)"
                    @keydown.enter="commitEdit(plan)"
                    @keydown.escape="cancelEdit"
                    :ref="(el) => el && el.focus()"
                  />
                  <span
                    v-if="editingPlanId !== plan.id || editingField !== 'type'"
                    class="tag editable-tag"
                    :class="planTypeClass(plan.type)"
                    @dblclick="startEdit(plan, 'type')"
                    :title="'双击编辑类型'"
                  >{{ displayPlanType(plan.type) }}</span>
                  <el-select
                    v-else
                    v-model="editBuffer"
                    size="small"
                    style="width: 100px"
                    @change="commitEdit(plan)"
                    @blur="commitEdit(plan)"
                    :ref="(el) => el && el.focus()"
                  >
                    <el-option v-for="t in planTypes" :key="t" :label="t" :value="t" />
                  </el-select>
                </div>
                <div class="plan-time">
                  <span
                    v-if="editingPlanId !== plan.id || editingField !== 'time'"
                    @dblclick="startEdit(plan, 'time')"
                    class="editable-text"
                    :title="'双击编辑时间'"
                  >{{ formatPlanTime(plan) }}</span>
                  <el-input
                    v-else
                    v-model="editBuffer"
                    size="small"
                    style="width: 100px"
                    placeholder="09:00-10:00"
                    @blur="commitEdit(plan)"
                    @keydown.enter="commitEdit(plan)"
                    @keydown.escape="cancelEdit"
                    :ref="(el) => el && el.focus()"
                  />
                  <el-icon class="delete-plan" @click="removePlan(plan)"><Close /></el-icon>
                </div>
              </div>
              <div class="add-plan-btn" @click="addPlan">
                <el-icon><Plus /></el-icon>
                <span>添加任务</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="panel-card">
            <div class="middle-header">
              <div>知识点掌握度</div>
            </div>
            <div v-if="hasMasteryData" class="mastery-content">
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
            <el-empty v-else description="暂无题库掌握数据" />
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="panel-card">
            <div class="middle-header">
              <div>薄弱知识点 Top5</div>
              <div class="more-link">更多 <el-icon><ArrowRight /></el-icon></div>
            </div>
            <div class="weak-list">
              <el-empty v-if="userWeakPoints.length === 0" description="暂无薄弱知识点，点击下方添加" />
              <div v-else class="weak-item" v-for="(point, idx) in userWeakPoints" :key="idx">
                <div class="weak-title">
                  <span
                    v-if="editingWeakId !== idx"
                    @dblclick="startWeakEdit(idx, point)"
                    class="editable-text"
                    :title="'双击编辑'"
                  >{{ point.name }}</span>
                  <el-input
                    v-else
                    v-model="weakEditName"
                    size="small"
                    style="width: 140px"
                    @blur="commitWeakEdit(idx)"
                    @keydown.enter="commitWeakEdit(idx)"
                    @keydown.escape="editingWeakId = -1"
                    :ref="(el) => el && el.focus()"
                  />
                  <div style="display:flex;align-items:center;gap:8px">
                    <span
                      v-if="editingWeakId !== idx"
                      @dblclick="startWeakEdit(idx, point)"
                      class="editable-text"
                    >{{ point.mastery }}%</span>
                    <el-input-number
                      v-else
                      v-model="weakEditMastery"
                      size="small"
                      :min="0"
                      :max="100"
                      style="width: 80px"
                      @blur="commitWeakEdit(idx)"
                      @keydown.enter="commitWeakEdit(idx)"
                      :ref="(el) => el && el.focus()"
                    />
                    <el-icon class="delete-plan" @click="removeWeakPoint(idx)"><Close /></el-icon>
                  </div>
                </div>
                <div class="weak-progress" :class="{ orange: point.mastery >= 50, yellow: point.mastery >= 60 }">
                  <span :style="{ width: `${point.mastery}%` }"></span>
                </div>
              </div>
              <div class="add-plan-btn" @click="addWeakPoint">
                <el-icon><Plus /></el-icon>
                <span>添加薄弱点</span>
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
              <el-empty v-if="recentExperiences.length === 0" description="暂无面试记录" />
              <div v-else class="table-row" v-for="record in recentExperiences" :key="record.id">
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
              <el-tooltip
                v-for="action in quickActions"
                :key="action.label"
                :content="action.disabled ? '施工中...' : ''"
                :disabled="!action.disabled"
                placement="top"
              >
                <div
                  :class="['quick-item', { disabled: action.disabled }]"
                  @click="handleQuickAction(action)"
                >
                  <el-icon :class="action.color"><component :is="action.icon" /></el-icon>
                  <span>{{ action.label }}</span>
                </div>
              </el-tooltip>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>

</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi, experienceApi } from '@/api/front'
import { ElMessage } from 'element-plus'

const router = useRouter()

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

// ——— 每日计划重置 ———
const PLAN_DATE_KEY = 'offerpilot_plan_date'

function todayKey() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function checkDailyReset() {
  const stored = localStorage.getItem(PLAN_DATE_KEY)
  const today = todayKey()
  if (stored !== today) {
    todayPlans.splice(0, todayPlans.length)
    localStorage.setItem(PLAN_DATE_KEY, today)
  }
}

// ——— 计划编辑状态 ———
const editingPlanId = ref('')
const editingField = ref('')
const editBuffer = ref('')

const planTypes = ['知识点', '算法', '项目', '模拟面试', '复盘']

function startEdit(plan, field) {
  editingPlanId.value = plan.id
  editingField.value = field
  editBuffer.value = field === 'time' ? '' : (plan[field] || '')
}

function commitEdit(plan) {
  const field = editingField.value
  if (field === 'type') {
    plan.type = editBuffer.value || plan.type
  } else if (field === 'time') {
    const parts = editBuffer.value.split('-').map(s => s.trim())
    if (parts.length === 2) {
      plan.startTime = parts[0]
      plan.endTime = parts[1]
    }
  } else {
    plan[field] = editBuffer.value.trim() || plan[field]
  }
  editingPlanId.value = ''
  editingField.value = ''
  savePlan(plan)
}

function cancelEdit() {
  editingPlanId.value = ''
  editingField.value = ''
}

async function savePlan(plan) {
  try {
    await dashboardApi.updateTodayPlan(plan.id, {
      title: plan.title,
      type: plan.type,
      startTime: plan.startTime,
      endTime: plan.endTime,
      completed: plan.completed
    })
  } catch { /* silent */ }
}

async function addPlan() {
  const newPlan = {
    id: 'plan_' + Date.now().toString(36),
    title: '新任务',
    type: '知识点',
    startTime: '09:00',
    endTime: '10:00',
    completed: false
  }
  todayPlans.push(newPlan)
  try {
    await dashboardApi.updateTodayPlan(newPlan.id, newPlan)
  } catch { /* silent */ }
}

async function removePlan(plan) {
  const idx = todayPlans.indexOf(plan)
  if (idx >= 0) todayPlans.splice(idx, 1)
}

// ——— 用户自定义薄弱点 ———
const WEAK_KEY = 'offerpilot_weak_points'

const userWeakPoints = reactive(loadWeakPoints())

function loadWeakPoints() {
  try {
    const raw = localStorage.getItem(WEAK_KEY)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore */ }
  return [
    { name: 'Vue3 响应式原理', mastery: 40 },
    { name: '虚拟 DOM', mastery: 45 },
    { name: '组件通信', mastery: 50 },
    { name: 'TypeScript 泛型', mastery: 60 },
    { name: '工程化构建', mastery: 65 }
  ]
}

function saveWeakPoints() {
  localStorage.setItem(WEAK_KEY, JSON.stringify(userWeakPoints))
}

const editingWeakId = ref(-1)
const weakEditName = ref('')
const weakEditMastery = ref(0)

function startWeakEdit(idx, point) {
  editingWeakId.value = idx
  weakEditName.value = point.name
  weakEditMastery.value = point.mastery
}

function commitWeakEdit(idx) {
  const name = weakEditName.value.trim()
  if (name) {
    if (idx >= 0 && idx < userWeakPoints.length) {
      userWeakPoints[idx].name = name
      userWeakPoints[idx].mastery = Math.min(100, Math.max(0, Number(weakEditMastery.value) || 0))
    }
  }
  editingWeakId.value = -1
  saveWeakPoints()
}

function addWeakPoint() {
  userWeakPoints.push({ name: '新知识点', mastery: 30 })
  saveWeakPoints()
}

function removeWeakPoint(idx) {
  userWeakPoints.splice(idx, 1)
  editingWeakId.value = -1
  saveWeakPoints()
}

// ——— 快捷操作 ———
const quickActions = [
  { label: '刷算法题', icon: 'Finished', color: 'blue', route: '/back/algorithm' },
  { label: '新建笔记', icon: 'Notebook', color: 'blue', route: '/back/question' },
  { label: '投递内推', icon: 'Promotion', color: 'blue', route: '/back/applications' },
  { label: '模拟面试', icon: 'User', color: 'orange', route: '/back/mock-interview' },
  { label: '知识点学习', icon: 'Reading', color: 'green', route: '', disabled: true },
  { label: '错题本', icon: 'Close', color: 'red', route: '', disabled: true },
  { label: '面经收集', icon: 'Tickets', color: 'blue', route: '/back/experience' },
  { label: '学习计划', icon: 'Calendar', color: 'blue', route: '', disabled: true }
]

function handleQuickAction(action) {
  if (action.disabled) return
  if (action.route) router.push(action.route)
}

const hasMasteryData = computed(() => {
  return Number(overview.mastery.overall || 0) > 0 || overview.weakPoints.length > 0
})

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
  if (Array.isArray(data.weakPoints)) {
    overview.weakPoints = data.weakPoints
  }
}

async function loadTodayPlans() {
  const data = await dashboardApi.getTodayPlan()
  if (Array.isArray(data)) {
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
  if (Array.isArray(list)) {
    recentExperiences.splice(0, recentExperiences.length, ...list.slice(0, 3))
  }
}

onMounted(async () => {
  checkDailyReset()
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
      display: flex;
      align-items: center;
      gap: 6px;
      color: #697386;
      font-size: 14px;
      text-align: right;
      white-space: nowrap;
      justify-content: flex-end;
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
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;

    &:hover:not(.disabled) {
      border-color: #2563eb;
      background: #eff6ff;
    }

    &.disabled {
      cursor: not-allowed;
      background-color: #f3f4f6;
      color: #9ca3af;

      .el-icon {
        opacity: 0.4;
      }
    }

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

  .editable-text {
    cursor: text;
    padding: 2px 4px;
    border-radius: 3px;
    transition: background 0.15s;

    &:hover {
      background: #e8f1ff;
    }
  }

  .editable-tag {
    cursor: pointer;
  }

  .delete-plan {
    color: #94a3b8;
    font-size: 14px;
    cursor: pointer;
    flex-shrink: 0;
    transition: color 0.15s;

    &:hover {
      color: #ef4444;
    }
  }

  .add-plan-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px;
    margin-top: 4px;
    border: 1px dashed #cbd5e1;
    border-radius: 6px;
    color: #667085;
    font-size: 14px;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s, background 0.15s;

    &:hover {
      border-color: #2563eb;
      color: #2563eb;
      background: #f8faff;
    }
  }
}
</style>
