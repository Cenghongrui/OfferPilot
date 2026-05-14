<template>
  <div class="op-page applications">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">Application Kanban</div>
        <h1 class="op-title">投递看板</h1>
        <p class="op-subtitle">用横向看板管理实习投递流程，拖动卡片即可同步当前阶段和下一步动作。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Plus" @click="dialogVisible = true">新增投递</el-button>
        <el-button :icon="RefreshLeft" :disabled="!lastMove" @click="undoMove">撤销移动</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="kanban">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="kanban-column"
        @dragover.prevent
        @drop="dropCard(stage.key)"
      >
        <div class="column-header">
          <strong>{{ stage.label }}</strong>
          <span>{{ cardsByStage(stage.key).length }}</span>
        </div>
        <div class="column-list">
          <article
            v-for="card in cardsByStage(stage.key)"
            :key="card.id"
            class="application-card"
            draggable="true"
            @dragstart="dragCard(card)"
          >
            <div class="op-row">
              <strong>{{ card.company }}</strong>
              <span class="op-tag">{{ card.city }}</span>
            </div>
            <p>{{ card.role }}</p>
            <div class="card-meta">
              <span>{{ card.source }}</span>
              <span>截止 {{ card.deadline }}</span>
            </div>
            <div class="next-action">{{ card.nextAction }}</div>
            <p class="notes">{{ card.notes }}</p>
          </article>
        </div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" title="新增投递记录" width="560px">
      <el-form label-width="88px">
        <el-form-item label="公司名称">
          <el-input v-model="draft.company" />
        </el-form-item>
        <el-form-item label="岗位名称">
          <el-input v-model="draft.role" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="draft.city" />
        </el-form-item>
        <el-form-item label="投递渠道">
          <el-input v-model="draft.source" />
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="draft.stage" style="width: 100%">
            <el-option v-for="stage in stages" :key="stage.key" :label="stage.label" :value="stage.key" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addApplication">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Plus, RefreshLeft } from '@element-plus/icons-vue'
import { applicationApi } from '@/api/front'

const stages = [
  { key: 'todo', label: '待投递' },
  { key: 'applied', label: '已投递' },
  { key: 'exam', label: '笔试' },
  { key: 'interview_1', label: '一面' },
  { key: 'interview_2', label: '二面' },
  { key: 'hr', label: 'HR 面' },
  { key: 'offer', label: 'Offer' },
  { key: 'closed', label: '已结束' }
]

const applications = reactive([
  {
    id: 'app_001',
    company: '腾讯',
    role: '前端开发实习生',
    city: '深圳',
    source: '官网',
    stage: 'interview_1',
    deadline: '2026-05-30',
    nextAction: '准备 Vue 项目深挖',
    notes: '重点复习组件通信和权限路由'
  },
  {
    id: 'app_002',
    company: '字节跳动',
    role: 'Web 前端实习生',
    city: '上海',
    source: '内推',
    stage: 'exam',
    deadline: '2026-05-22',
    nextAction: '完成在线笔试',
    notes: '算法准备滑动窗口和二叉树'
  },
  {
    id: 'app_003',
    company: '美团',
    role: '前端工程师实习生',
    city: '北京',
    source: '牛客',
    stage: 'applied',
    deadline: '2026-05-25',
    nextAction: '等待筛选结果',
    notes: '补充项目性能优化亮点'
  },
  {
    id: 'app_004',
    company: '阿里巴巴',
    role: '前端开发实习生',
    city: '杭州',
    source: '校招官网',
    stage: 'offer',
    deadline: '2026-06-01',
    nextAction: '确认实习时间',
    notes: '已通过二面和 HR 面'
  }
])

const dialogVisible = ref(false)
const dragging = ref(null)
const lastMove = ref(null)
const remoteStats = ref(null)
const draft = reactive({
  company: '小红书',
  role: '前端开发实习生',
  city: '上海',
  source: 'Boss 直聘',
  stage: 'todo'
})

const stats = computed(() => [
  { label: '投递总数', value: remoteStats.value?.total ?? applications.length },
  {
    label: '面试中',
    value: remoteStats.value?.interviewing ?? applications.filter((item) => ['interview_1', 'interview_2', 'hr'].includes(item.stage)).length
  },
  { label: 'Offer', value: remoteStats.value?.offer ?? applications.filter((item) => item.stage === 'offer').length }
])

function cardsByStage(stage) {
  return applications.filter((item) => item.stage === stage)
}

function dragCard(card) {
  dragging.value = card
}

async function dropCard(stage) {
  if (!dragging.value || dragging.value.stage === stage) return
  const card = dragging.value
  const fromStage = card.stage
  lastMove.value = { id: card.id, from: fromStage, to: stage }
  card.stage = stage
  dragging.value = null
  try {
    await applicationApi.move(card.id, {
      fromStage,
      toStage: stage,
      sortOrder: card.sortOrder || 1000
    })
    await loadStats()
  } catch {
    card.stage = fromStage
    lastMove.value = null
  }
}

async function undoMove() {
  if (!lastMove.value) return
  const card = applications.find((item) => item.id === lastMove.value.id)
  if (card) {
    const move = lastMove.value
    card.stage = move.from
    await applicationApi.move(card.id, {
      fromStage: move.to,
      toStage: move.from,
      sortOrder: card.sortOrder || 1000
    })
    await loadStats()
  }
  lastMove.value = null
}

async function addApplication() {
  const created = await applicationApi.create({
    company: draft.company,
    role: draft.role,
    city: draft.city,
    source: draft.source,
    stage: draft.stage,
    deadline: '2026-06-15',
    nextAction: '补充简历并跟进进度',
  })
  applications.unshift(created)
  dialogVisible.value = false
  await loadStats()
}

function replaceApplications(list) {
  if (!Array.isArray(list) || list.length === 0) return
  applications.splice(0, applications.length, ...list)
}

async function loadApplications() {
  const result = await applicationApi.getList()
  replaceApplications(result.list || result)
}

async function loadStats() {
  remoteStats.value = await applicationApi.getStats()
}

onMounted(async () => {
  await Promise.all([loadApplications(), loadStats()])
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.kanban {
  display: grid;
  grid-auto-columns: 280px;
  grid-auto-flow: column;
  gap: 14px;
  min-height: 560px;
  overflow-x: auto;
  padding-bottom: 12px;
}

.kanban-column {
  display: flex;
  flex-direction: column;
  min-height: 540px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.column-header span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 6px;
  color: #2563eb;
  background: #eff6ff;
  font-size: 12px;
  font-weight: 800;
}

.column-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
}

.application-card {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  cursor: grab;
}

.application-card:active {
  cursor: grabbing;
}

.application-card p {
  margin-top: 8px;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
  color: #667085;
  font-size: 12px;
}

.next-action {
  margin-top: 12px;
  padding: 10px;
  border-radius: 6px;
  color: #1d4ed8;
  background: #eff6ff;
  font-size: 13px;
  font-weight: 700;
}

.notes {
  color: #667085;
  font-size: 13px;
}
</style>
