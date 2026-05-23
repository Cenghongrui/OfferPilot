<template>
  <div class="op-page questions">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">面试题库</div>
        <h1 class="op-title">面试题库</h1>
        <p class="op-subtitle">按 CSS、JavaScript、Vue、网络和算法分类沉淀高频面试题，支持自定义新增、编辑、搜索、收藏和掌握状态维护。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增面试题</el-button>
        <el-button :icon="Refresh" @click="reloadAll">刷新题库</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid main-grid">
      <div class="op-card pad list-panel">
        <div class="op-section-title">
          <span>题目列表</span>
          <span class="op-muted">{{ filteredQuestions.length }} 道</span>
        </div>
        <div class="op-toolbar">
          <el-input v-model="keyword" clearable placeholder="搜索题目、标签或答案" :prefix-icon="Search" />
          <el-select v-model="difficulty" placeholder="难度" style="width: 120px">
            <el-option label="全部" value="all" />
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
          <el-checkbox v-model="onlyStarred">只看收藏</el-checkbox>
          <el-checkbox v-model="onlyUnmastered">待掌握</el-checkbox>
        </div>

        <div class="category-tabs">
          <button
            v-for="category in categories"
            :key="category"
            :class="{ active: currentCategory === category }"
            @click="currentCategory = category"
          >
            {{ category }}
          </button>
        </div>

        <el-empty v-if="filteredQuestions.length === 0" description="暂无面试题，点击右上角新增一题" />

        <div v-else class="op-list question-list">
          <article
            v-for="question in filteredQuestions"
            :key="question.id"
            class="op-list-item"
            :class="{ active: question.id === selectedQuestion?.id }"
            @click="selectedId = question.id"
          >
            <div class="op-row">
              <strong>{{ question.title }}</strong>
              <el-button link :icon="question.starred ? StarFilled : Star" @click.stop="toggleStar(question)" />
            </div>
            <div class="op-tags">
              <span class="op-tag">{{ question.category }}</span>
              <span class="op-tag orange">{{ difficultyMap[question.difficulty] || '未设置' }}</span>
              <span class="op-tag green" v-if="question.mastered">已掌握</span>
              <span class="op-tag red" v-else>待复习</span>
            </div>
            <p class="last-review">上次复习：{{ question.lastReviewedAt || '暂无记录' }}</p>
          </article>
        </div>
      </div>

      <aside class="op-card pad op-detail">
        <template v-if="selectedQuestion">
          <div class="op-section-title">
            <span>题目详情</span>
            <div class="detail-actions">
              <el-switch
                v-model="selectedQuestion.mastered"
                active-text="已掌握"
                inactive-text="待复习"
                @change="updateMastery(selectedQuestion)"
              />
              <el-button link type="primary" :icon="Edit" @click="openEditDialog(selectedQuestion)">编辑</el-button>
            </div>
          </div>
          <h3>{{ selectedQuestion.title }}</h3>
          <p>{{ selectedQuestion.answer || '还没有填写参考答案。' }}</p>

          <div class="detail-block">
            <strong>追问</strong>
            <ul v-if="selectedQuestion.followUps?.length">
              <li v-for="item in selectedQuestion.followUps" :key="item">{{ item }}</li>
            </ul>
            <p v-else class="op-muted">暂无追问。</p>
          </div>
          <div class="detail-block">
            <strong>易错点</strong>
            <ul v-if="selectedQuestion.pitfalls?.length">
              <li v-for="item in selectedQuestion.pitfalls" :key="item">{{ item }}</li>
            </ul>
            <p v-else class="op-muted">暂无易错点。</p>
          </div>
          <el-input
            v-model="selectedQuestion.note"
            type="textarea"
            :rows="5"
            placeholder="写下自己的补充笔记"
            @blur="saveNote(selectedQuestion)"
          />
        </template>
        <el-empty v-else description="选择或新增一道面试题后查看详情" />
      </aside>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑面试题' : '新增面试题'" width="680px">
      <el-form label-width="88px">
        <el-form-item label="题目" required>
          <el-input v-model="form.title" placeholder="例如：Vue3 响应式原理是什么？" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="category in categoriesWithoutAll" :key="category" :label="category" :value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-radio-group v-model="form.difficulty">
            <el-radio-button value="easy">简单</el-radio-button>
            <el-radio-button value="medium">中等</el-radio-button>
            <el-radio-button value="hard">困难</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tagsText" placeholder="多个标签用逗号分隔，例如：Vue, 响应式, Proxy" />
        </el-form-item>
        <el-form-item label="参考答案">
          <el-input v-model="form.answer" type="textarea" :rows="4" placeholder="写一版面试时可以讲的参考答案" />
        </el-form-item>
        <el-form-item label="追问">
          <el-input v-model="form.followUpsText" type="textarea" :rows="3" placeholder="每行一个追问" />
        </el-form-item>
        <el-form-item label="易错点">
          <el-input v-model="form.pitfallsText" type="textarea" :rows="3" placeholder="每行一个易错点" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuestion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Plus, Refresh, Search, Star, StarFilled } from '@element-plus/icons-vue'
import { questionApi } from '@/api/front'

const categories = ['全部', 'CSS', 'JavaScript', 'Vue', 'Network', 'Algorithm']
const categoriesWithoutAll = categories.filter((item) => item !== '全部')
const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }

const questions = reactive([])
const keyword = ref('')
const difficulty = ref('all')
const currentCategory = ref('全部')
const onlyStarred = ref(false)
const onlyUnmastered = ref(false)
const selectedId = ref('')
const remoteStats = ref({ total: 0, starred: 0, reviewTodo: 0 })
const dialogVisible = ref(false)
const editingId = ref('')
const form = reactive({
  title: '',
  category: 'Vue',
  difficulty: 'medium',
  tagsText: '',
  answer: '',
  followUpsText: '',
  pitfallsText: ''
})

const filteredQuestions = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  return questions.filter((item) => {
    const tags = Array.isArray(item.tags) ? item.tags : []
    const hitKeyword = !text || [item.title, item.answer, ...tags].join(' ').toLowerCase().includes(text)
    const hitCategory = currentCategory.value === '全部' || item.category === currentCategory.value
    const hitDifficulty = difficulty.value === 'all' || item.difficulty === difficulty.value
    const hitStarred = !onlyStarred.value || item.starred
    const hitMastered = !onlyUnmastered.value || !item.mastered
    return hitKeyword && hitCategory && hitDifficulty && hitStarred && hitMastered
  })
})

const selectedQuestion = computed(() => {
  return questions.find((item) => item.id === selectedId.value) || filteredQuestions.value[0] || null
})

const stats = computed(() => [
  { label: '题库总量', value: remoteStats.value?.total ?? questions.length },
  { label: '收藏题目', value: remoteStats.value?.starred ?? questions.filter((item) => item.starred).length },
  { label: '待复习', value: remoteStats.value?.reviewTodo ?? questions.filter((item) => !item.mastered).length }
])

function splitLines(value) {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
}

function splitTags(value) {
  return value
    .split(/[,，]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function resetForm() {
  Object.assign(form, {
    title: '',
    category: 'Vue',
    difficulty: 'medium',
    tagsText: '',
    answer: '',
    followUpsText: '',
    pitfallsText: ''
  })
}

function openCreateDialog() {
  editingId.value = ''
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(question) {
  editingId.value = question.id
  Object.assign(form, {
    title: question.title || '',
    category: question.category || 'Vue',
    difficulty: question.difficulty || 'medium',
    tagsText: (question.tags || []).join('，'),
    answer: question.answer || '',
    followUpsText: (question.followUps || []).join('\n'),
    pitfallsText: (question.pitfalls || []).join('\n')
  })
  dialogVisible.value = true
}

function buildPayload() {
  return {
    title: form.title.trim(),
    category: form.category,
    difficulty: form.difficulty,
    tags: splitTags(form.tagsText),
    answer: form.answer.trim(),
    followUps: splitLines(form.followUpsText),
    pitfalls: splitLines(form.pitfallsText),
    mastered: false,
    starred: false,
    note: '',
    lastReviewedAt: ''
  }
}

function replaceQuestions(list) {
  if (!Array.isArray(list)) return
  questions.splice(0, questions.length, ...list)
  selectedId.value = list[0]?.id || ''
}

async function loadQuestions() {
  const result = await questionApi.getList({ page: 1, pageSize: 100 })
  replaceQuestions(result.list || result)
}

async function loadStats() {
  remoteStats.value = await questionApi.getStats()
}

async function reloadAll() {
  await Promise.all([loadQuestions(), loadStats()])
}

async function submitQuestion() {
  if (!form.title.trim()) {
    ElMessage.warning('请先填写题目')
    return
  }
  const payload = buildPayload()
  if (editingId.value) {
    const current = questions.find((item) => item.id === editingId.value)
    const updated = await questionApi.update(editingId.value, {
      ...payload,
      mastered: current?.mastered ?? false,
      starred: current?.starred ?? false,
      note: current?.note ?? '',
      lastReviewedAt: current?.lastReviewedAt ?? ''
    })
    if (current) Object.assign(current, updated)
    selectedId.value = updated.id
    ElMessage.success('面试题已更新')
  } else {
    const created = await questionApi.create(payload)
    questions.unshift(created)
    selectedId.value = created.id
    ElMessage.success('面试题已新增')
  }
  dialogVisible.value = false
  await loadStats()
}

async function toggleStar(question) {
  const nextStarred = !question.starred
  question.starred = nextStarred
  try {
    await questionApi.updateStar(question.id, { starred: nextStarred })
    await loadStats()
  } catch {
    question.starred = !nextStarred
  }
}

async function updateMastery(question) {
  if (!question?.id) return
  const lastReviewedAt = new Date().toISOString().slice(0, 10)
  await questionApi.updateMastery(question.id, {
    mastered: question.mastered,
    lastReviewedAt
  })
  question.lastReviewedAt = lastReviewedAt
  await loadStats()
}

async function saveNote(question) {
  if (!question?.id) return
  await questionApi.update(question.id, { note: question.note })
}

onMounted(reloadAll)
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.main-grid {
  grid-template-columns: 320px minmax(0, 1fr);
}

.list-panel {
  overflow: hidden;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.category-tabs button {
  height: 32px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #475467;
  background: #fff;
  cursor: pointer;
}

.category-tabs button.active {
  color: #fff;
  border-color: #2563eb;
  background: #2563eb;
}

.question-list {
  max-height: calc(100vh - 350px);
  overflow: auto;
}

.last-review {
  margin-top: 10px;
  color: #667085;
  font-size: 13px;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-block {
  margin: 18px 0;
}

.detail-block strong {
  display: block;
  margin-bottom: 8px;
}

.detail-block ul {
  margin: 0;
  padding-left: 18px;
  color: #475467;
  line-height: 1.8;
}

@media (max-width: 1100px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
</style>
