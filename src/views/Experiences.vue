<template>
  <div class="op-page experiences">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">面经笔记</div>
        <h1 class="op-title">面经笔记</h1>
        <p class="op-subtitle">把真实面试、牛客面经和日常复盘整理成可持续维护的面经库，支持新增、编辑、阶段流转和结果标记。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增面经</el-button>
        <el-button :icon="Download" @click="exportExperiences">导出 JSON</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid experiences-layout">
      <aside class="op-card pad">
        <div class="op-section-title">
          <span>公司列表</span>
          <el-select v-model="roundFilter" style="width: 120px">
            <el-option label="全部" value="all" />
            <el-option v-for="round in timeline" :key="round" :label="round" :value="round" />
          </el-select>
        </div>

        <el-empty v-if="filteredExperiences.length === 0" description="暂无面经，点击右上角新增一条" />

        <div v-else class="op-list">
          <article
            v-for="item in filteredExperiences"
            :key="item.id"
            class="op-list-item"
            :class="{ active: item.id === selectedId }"
            @click="selectedId = item.id"
          >
            <div class="op-row">
              <strong>{{ item.company }}</strong>
              <span class="op-tag" :class="resultClass(item.result)">{{ resultMap[item.result] || '跟进中' }}</span>
            </div>
            <p class="meta">{{ item.role }} / {{ item.city || '未填写城市' }} / {{ item.date || '未填写日期' }}</p>
            <div class="op-tags">
              <span class="op-tag orange">{{ item.round }}</span>
              <span v-for="group in questionGroups(item)" :key="group" class="op-tag">{{ group }}</span>
            </div>
          </article>
        </div>
      </aside>

      <main class="op-card pad op-detail">
        <template v-if="current">
          <div class="op-section-title">
            <span>{{ current.company }} / {{ current.role }}</span>
            <div class="detail-actions">
              <el-button link type="primary" :icon="Edit" @click="openEditDialog(current)">编辑</el-button>
              <el-button link type="primary" @click="saveExperience(current)">保存</el-button>
            </div>
          </div>

          <div class="status-row">
            <span>面试结果</span>
            <el-radio-group v-model="current.result" size="small" @change="updateResult(current)">
              <el-radio-button value="pending">跟进中</el-radio-button>
              <el-radio-button value="passed">已通过</el-radio-button>
              <el-radio-button value="failed">已挂</el-radio-button>
            </el-radio-group>
          </div>

          <div class="timeline">
            <button
              v-for="step in timeline"
              :key="step"
              class="timeline-step"
              :class="{ active: step === current.round, done: stepIndex(step) < stepIndex(current.round) }"
              @click="changeRound(step)"
            >
              <span></span>
              <strong>{{ step }}</strong>
            </button>
          </div>

          <div class="question-groups">
            <div v-for="question in current.questions" :key="question.content" class="question-chip">
              <span>{{ question.category }}</span>
              <p>{{ question.content }}</p>
            </div>
          </div>

          <div class="review-grid">
            <div>
              <strong>答得好的点</strong>
              <el-input v-model="current.review.good" type="textarea" :rows="3" @blur="saveExperience(current)" />
            </div>
            <div>
              <strong>卡住的点</strong>
              <el-input v-model="current.review.stuck" type="textarea" :rows="3" @blur="saveExperience(current)" />
            </div>
            <div>
              <strong>下次改进</strong>
              <el-input v-model="current.review.action" type="textarea" :rows="3" @blur="saveExperience(current)" />
            </div>
          </div>

          <el-input v-model="current.markdown" type="textarea" :rows="7" placeholder="Markdown 复盘笔记" @blur="saveExperience(current)" />
        </template>
        <el-empty v-else description="选择或新增一条面经后查看详情" />
      </main>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑面经' : '新增面经'" width="720px">
      <el-form label-width="88px">
        <el-form-item label="公司" required>
          <el-input v-model="form.company" />
        </el-form-item>
        <el-form-item label="岗位" required>
          <el-input v-model="form.role" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="form.city" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="轮次">
          <el-select v-model="form.round" style="width: 100%">
            <el-option v-for="round in timeline" :key="round" :label="round" :value="round" />
          </el-select>
        </el-form-item>
        <el-form-item label="结果">
          <el-radio-group v-model="form.result">
            <el-radio-button value="pending">跟进中</el-radio-button>
            <el-radio-button value="passed">已通过</el-radio-button>
            <el-radio-button value="failed">已挂</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="面试问题">
          <el-input v-model="form.questionsText" type="textarea" :rows="4" placeholder="每行一个问题，格式可写：Vue：Vue3 响应式原理是什么？" />
        </el-form-item>
        <el-form-item label="复盘笔记">
          <el-input v-model="form.markdown" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitExperience">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Edit, Plus } from '@element-plus/icons-vue'
import { experienceApi } from '@/api/front'

const timeline = ['一面', '二面', 'HR 面', 'Offer']
const resultMap = { pending: '跟进中', passed: '已通过', failed: '已挂' }
const roundFilter = ref('all')
const selectedId = ref('')
const dialogVisible = ref(false)
const editingId = ref('')
const remoteStats = ref({ total: 0, pending: 0, passed: 0 })
const experiences = reactive([])
const form = reactive({
  company: '',
  role: '',
  city: '',
  date: new Date().toISOString().slice(0, 10),
  round: '一面',
  result: 'pending',
  questionsText: '',
  markdown: ''
})

const filteredExperiences = computed(() => {
  if (roundFilter.value === 'all') return experiences
  return experiences.filter((item) => item.round === roundFilter.value)
})

const current = computed(() => experiences.find((item) => item.id === selectedId.value) || filteredExperiences.value[0] || null)

const stats = computed(() => [
  { label: '面经数量', value: remoteStats.value?.total ?? experiences.length },
  { label: '跟进中', value: remoteStats.value?.pending ?? experiences.filter((item) => item.result === 'pending').length },
  { label: '已通过', value: remoteStats.value?.passed ?? experiences.filter((item) => item.result === 'passed').length }
])

function questionGroups(item) {
  return [...new Set((item.questions || []).map((question) => question.category))]
}

function resultClass(result) {
  if (result === 'passed') return 'green'
  if (result === 'failed') return 'red'
  return 'orange'
}

function stepIndex(step) {
  return timeline.indexOf(step)
}

function parseQuestions(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const matched = line.match(/^(.+?)[:：](.+)$/)
      if (!matched) return { category: '未分类', content: line }
      return { category: matched[1].trim(), content: matched[2].trim() }
    })
}

function questionsToText(questions = []) {
  return questions.map((item) => `${item.category}：${item.content}`).join('\n')
}

function resetForm() {
  Object.assign(form, {
    company: '',
    role: '',
    city: '',
    date: new Date().toISOString().slice(0, 10),
    round: '一面',
    result: 'pending',
    questionsText: '',
    markdown: ''
  })
}

function openCreateDialog() {
  editingId.value = ''
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(item) {
  editingId.value = item.id
  Object.assign(form, {
    company: item.company || '',
    role: item.role || '',
    city: item.city || '',
    date: item.date || new Date().toISOString().slice(0, 10),
    round: item.round || '一面',
    result: item.result || 'pending',
    questionsText: questionsToText(item.questions || []),
    markdown: item.markdown || ''
  })
  dialogVisible.value = true
}

function buildPayload() {
  return {
    company: form.company.trim(),
    role: form.role.trim(),
    city: form.city.trim(),
    date: form.date,
    round: form.round,
    result: form.result,
    questions: parseQuestions(form.questionsText),
    review: { good: '待补充', stuck: '待补充', action: '待补充' },
    markdown: form.markdown
  }
}

function refreshStatsFromList() {
  remoteStats.value = {
    total: experiences.length,
    pending: experiences.filter((item) => item.result === 'pending').length,
    passed: experiences.filter((item) => item.result === 'passed').length
  }
}

function replaceExperiences(list) {
  if (!Array.isArray(list)) return
  experiences.splice(0, experiences.length, ...list)
  selectedId.value = list[0]?.id || ''
  refreshStatsFromList()
}

async function loadExperiences() {
  const result = await experienceApi.getList({ page: 1, pageSize: 100 })
  replaceExperiences(result.list || result)
}

async function submitExperience() {
  if (!form.company.trim() || !form.role.trim()) {
    ElMessage.warning('请填写公司和岗位')
    return
  }
  const payload = buildPayload()
  if (editingId.value) {
    const currentItem = experiences.find((item) => item.id === editingId.value)
    const updated = await experienceApi.update(editingId.value, {
      ...currentItem,
      ...payload,
      review: currentItem?.review || payload.review
    })
    if (currentItem) Object.assign(currentItem, updated)
    selectedId.value = updated.id
    ElMessage.success('面经已更新')
  } else {
    const created = await experienceApi.create(payload)
    experiences.unshift(created)
    selectedId.value = created.id
    ElMessage.success('面经已新增')
  }
  dialogVisible.value = false
  refreshStatsFromList()
}

async function saveExperience(experience) {
  if (!experience?.id) return
  const updated = await experienceApi.update(experience.id, experience)
  Object.assign(experience, updated)
  refreshStatsFromList()
  ElMessage.success('面经已保存')
}

async function changeRound(round) {
  if (!current.value || current.value.round === round) return
  current.value.round = round
  await saveExperience(current.value)
}

async function updateResult(experience) {
  await saveExperience(experience)
}

async function exportExperiences() {
  const result = await experienceApi.exportJson()
  ElMessage.success(`已生成导出数据：${result.filename || 'experiences.json'}`)
}

onMounted(loadExperiences)
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.experiences-layout {
  grid-template-columns: 380px minmax(0, 1fr);
}

.meta {
  margin-top: 8px;
  color: #667085;
  font-size: 13px;
}

.detail-actions,
.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-row {
  justify-content: space-between;
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #f8fafc;
}

.timeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.timeline-step {
  position: relative;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #667085;
  text-align: left;
  background: #fff;
  cursor: pointer;
}

.timeline-step span {
  display: block;
  width: 10px;
  height: 10px;
  margin-bottom: 8px;
  border-radius: 50%;
  background: #d0d5dd;
}

.timeline-step.done span,
.timeline-step.active span {
  background: #2563eb;
}

.timeline-step.active {
  border-color: #2563eb;
  color: #172033;
  background: #eff6ff;
}

.question-groups {
  display: grid;
  gap: 10px;
  margin-bottom: 18px;
}

.question-chip {
  padding: 14px;
  border-radius: 8px;
  background: #f8fafc;
}

.question-chip span {
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
}

.question-chip p {
  margin-top: 6px;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}

.review-grid > div {
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.review-grid strong {
  display: block;
  margin-bottom: 8px;
}

@media (max-width: 1100px) {
  .experiences-layout,
  .timeline,
  .review-grid {
    grid-template-columns: 1fr;
  }

  .status-row {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
