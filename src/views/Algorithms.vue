<template>
  <div class="op-page algorithms">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">算法笔记</div>
        <h1 class="op-title">算法笔记</h1>
        <p class="op-subtitle">整理实习高频算法题，在同一页面记录题意、标签、代码模板、解题思路和复盘笔记，做题点击题目链接跳转。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增算法题</el-button>
        <el-button :icon="Refresh" @click="reloadAll">刷新</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid algo-layout">
      <aside class="op-card pad list-panel">
        <div class="op-section-title">
          <span>题目列表</span>
          <el-select v-model="filterStatus" style="width: 110px">
            <el-option label="全部" value="all" />
            <el-option label="未开始" value="todo" />
            <el-option label="进行中" value="doing" />
            <el-option label="已完成" value="done" />
          </el-select>
        </div>
        <el-empty v-if="filteredProblems.length === 0" description="暂无算法题" />
        <div v-else class="op-list algo-list">
          <article
            v-for="problem in filteredProblems"
            :key="problem.id"
            class="op-list-item"
            :class="{ active: problem.id === selectedId }"
            @click="selectedId = problem.id"
          >
            <div class="op-row">
              <strong>{{ problem.title }}</strong>
            </div>
            <div class="op-tags">
              <span class="op-tag" :class="difficultyClass(problem.difficulty)">{{ difficultyMap[problem.difficulty] || problem.difficulty }}</span>
              <span class="op-tag green" v-if="problem.status === 'done'">已完成</span>
              <span class="op-tag orange" v-else-if="problem.status === 'doing'">进行中</span>
              <span class="op-tag" v-else>未开始</span>
            </div>
          </article>
        </div>
      </aside>

      <main class="op-card pad op-detail detail-panel">
        <template v-if="currentProblem">
          <div class="op-section-title">
            <span>题目详情</span>
            <div>
              <el-select v-model="currentProblem.status" style="width: 110px" @change="saveProblem">
                <el-option label="未开始" value="todo" />
                <el-option label="进行中" value="doing" />
                <el-option label="已完成" value="done" />
              </el-select>
            </div>
          </div>

          <div class="detail-field">
            <label>题目名称</label>
            <el-input v-model="currentProblem.title" @blur="saveProblem" />
          </div>

          <div class="detail-field">
            <label>题目链接</label>
            <el-input v-model="currentProblem.leetcodeUrl" placeholder="https://leetcode.cn/problems/..." @blur="saveProblem" />
          </div>

          <div class="detail-field">
            <label>难度</label>
            <el-radio-group v-model="currentProblem.difficulty" @change="saveProblem">
              <el-radio-button value="easy">简单</el-radio-button>
              <el-radio-button value="medium">中等</el-radio-button>
              <el-radio-button value="hard">困难</el-radio-button>
            </el-radio-group>
          </div>

          <div class="detail-field">
            <label>标签</label>
            <el-input v-model="tagsText" placeholder="多个标签用逗号分隔" @blur="saveTags" />
          </div>

          <div class="detail-field">
            <label>题目描述</label>
            <el-input v-model="currentProblem.description" type="textarea" :rows="4" @blur="saveProblem" />
          </div>

          <div class="detail-field">
            <label>解题思路</label>
            <el-input v-model="currentProblem.idea" type="textarea" :rows="4" placeholder="记录解题思路、核心要点和复杂度分析" @blur="saveProblem" />
          </div>

          <div class="detail-field">
            <label>代码模板</label>
            <el-input
              v-model="currentProblem.codeDraft"
              type="textarea"
              :rows="12"
              spellcheck="false"
              class="code-editor"
              placeholder="记录代码模板或草稿"
              @blur="saveCodeDraft"
            />
          </div>

          <div class="detail-field">
            <label>复盘笔记</label>
            <el-input v-model="currentProblem.notes" type="textarea" :rows="4" placeholder="记录错因、易错点、二刷日期和优化方向" @blur="saveProblem" />
          </div>
        </template>
        <el-empty v-else description="选择或新增一道算法题后查看详情" />
      </main>
    </section>

    <el-dialog v-model="dialogVisible" title="新增算法题" width="560px">
      <el-form label-width="88px">
        <el-form-item label="题目名称" required>
          <el-input v-model="createForm.title" placeholder="例如：两数之和" />
        </el-form-item>
        <el-form-item label="题目链接">
          <el-input v-model="createForm.leetcodeUrl" placeholder="https://leetcode.cn/problems/..." />
        </el-form-item>
        <el-form-item label="难度">
          <el-radio-group v-model="createForm.difficulty">
            <el-radio-button value="easy">简单</el-radio-button>
            <el-radio-button value="medium">中等</el-radio-button>
            <el-radio-button value="hard">困难</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="createForm.tagsText" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="题目描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { algorithmApi } from '@/api/front'

const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }
const filterStatus = ref('all')
const selectedId = ref('')
const remoteStats = ref(null)
const dialogVisible = ref(false)

const problems = reactive([])

const createForm = reactive({
  title: '',
  leetcodeUrl: '',
  difficulty: 'medium',
  tagsText: '',
  description: ''
})

const filteredProblems = computed(() => {
  if (filterStatus.value === 'all') return problems
  return problems.filter((item) => item.status === filterStatus.value)
})

const currentProblem = computed(() => problems.find((item) => item.id === selectedId.value) || problems[0] || null)

const tagsText = ref('')

watch(currentProblem, (p) => {
  tagsText.value = (p?.tags || []).join('，')
}, { immediate: true })

watch(() => currentProblem.value?.tags, (t) => {
  if (t) tagsText.value = t.join('，')
})

const stats = computed(() => [
  { label: '题目总数', value: remoteStats.value?.total ?? problems.length },
  {
    label: '完成率',
    value: remoteStats.value?.completionRate
      ? `${remoteStats.value.completionRate}%`
      : `${problems.length ? Math.round((problems.filter((item) => item.status === 'done').length / problems.length) * 100) : 0}%`
  },
  { label: '本周复盘', value: remoteStats.value?.reviewCountThisWeek ?? problems.filter((item) => item.notes).length }
])

function difficultyClass(difficulty) {
  if (difficulty === 'easy') return 'green'
  if (difficulty === 'hard') return 'red'
  return 'orange'
}

function makeId() {
  return 'algo_' + Date.now().toString(36)
}

async function saveProblem() {
  if (!currentProblem.value) return
  try {
    await algorithmApi.update(currentProblem.value.id, {
      title: currentProblem.value.title,
      leetcodeUrl: currentProblem.value.leetcodeUrl,
      difficulty: currentProblem.value.difficulty,
      description: currentProblem.value.description,
      idea: currentProblem.value.idea,
      notes: currentProblem.value.notes,
      status: currentProblem.value.status
    })
  } catch {
    ElMessage.error('保存失败')
  }
}

async function saveTags() {
  if (!currentProblem.value) return
  currentProblem.value.tags = tagsText.value.split(/[,，]/).map(s => s.trim()).filter(Boolean)
  await saveProblem()
}

async function saveCodeDraft() {
  if (!currentProblem.value) return
  try {
    await algorithmApi.saveCodeDraft(currentProblem.value.id, {
      codeDraft: currentProblem.value.codeDraft
    })
  } catch {
    ElMessage.error('保存代码草稿失败')
  }
}

function openCreateDialog() {
  Object.assign(createForm, {
    title: '',
    leetcodeUrl: '',
    difficulty: 'medium',
    tagsText: '',
    description: ''
  })
  dialogVisible.value = true
}

async function submitCreate() {
  if (!createForm.title.trim()) {
    ElMessage.warning('请填写题目名称')
    return
  }
  const payload = {
    id: makeId(),
    title: createForm.title.trim(),
    leetcodeUrl: createForm.leetcodeUrl.trim(),
    difficulty: createForm.difficulty,
    tags: createForm.tagsText.split(/[,，]/).map(s => s.trim()).filter(Boolean),
    description: createForm.description.trim(),
    status: 'todo',
    idea: '',
    complexity: '',
    codeDraft: '',
    notes: '',
    testCases: []
  }
  try {
    const created = await algorithmApi.create(payload)
    problems.unshift(created)
    selectedId.value = created.id
    dialogVisible.value = false
    ElMessage.success('算法题已新增')
    await loadStats()
  } catch {
    ElMessage.error('新增失败')
  }
}

function replaceProblems(list) {
  if (!Array.isArray(list)) return
  problems.splice(0, problems.length, ...list)
  selectedId.value = list[0]?.id || ''
}

async function loadProblems() {
  const result = await algorithmApi.getList({ page: 1, pageSize: 100 })
  replaceProblems(result.list || result)
}

async function loadStats() {
  remoteStats.value = await algorithmApi.getStats()
}

async function reloadAll() {
  await Promise.all([loadProblems(), loadStats()])
}

onMounted(reloadAll)
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.algo-layout {
  grid-template-columns: 280px minmax(0, 1fr);
}

.list-panel {
  overflow: hidden;
}

.algo-list {
  max-height: calc(100vh - 350px);
  overflow: auto;
}

.detail-panel {
  overflow-y: auto;
  max-height: calc(100vh - 260px);
}

.detail-field {
  margin-bottom: 18px;
}

.detail-field label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #172033;
}

.code-editor :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 1100px) {
  .algo-layout {
    grid-template-columns: 1fr;
  }
}
</style>
