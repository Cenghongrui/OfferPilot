<template>
  <div class="op-page experiences">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">Interview Notes</div>
        <h1 class="op-title">面经笔记</h1>
        <p class="op-subtitle">把真实面试、牛客面经和日常笔记整理成可复盘的公司面经库。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Plus" @click="dialogVisible = true">新增面经</el-button>
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
            <el-option label="一面" value="一面" />
            <el-option label="二面" value="二面" />
            <el-option label="HR 面" value="HR 面" />
          </el-select>
        </div>

        <div class="op-list">
          <article
            v-for="item in filteredExperiences"
            :key="item.id"
            class="op-list-item"
            :class="{ active: item.id === selectedId }"
            @click="selectedId = item.id"
          >
            <div class="op-row">
              <strong>{{ item.company }}</strong>
              <span class="op-tag" :class="resultClass(item.result)">{{ resultMap[item.result] }}</span>
            </div>
            <p class="meta">{{ item.role }} · {{ item.city }} · {{ item.date }}</p>
            <div class="op-tags">
              <span class="op-tag orange">{{ item.round }}</span>
              <span v-for="group in questionGroups(item)" :key="group" class="op-tag">{{ group }}</span>
            </div>
          </article>
        </div>
      </aside>

      <main class="op-card pad op-detail">
        <div class="op-section-title">
          <span>{{ current.company }} / {{ current.role }}</span>
          <el-button link type="primary" :icon="Edit" @click="saveExperience(current)">保存</el-button>
        </div>

        <div class="timeline">
          <div
            v-for="step in timeline"
            :key="step"
            class="timeline-step"
            :class="{ active: step === current.round, done: stepIndex(step) < stepIndex(current.round) }"
          >
            <span></span>
            <strong>{{ step }}</strong>
          </div>
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
            <p>{{ current.review.good }}</p>
          </div>
          <div>
            <strong>卡住的点</strong>
            <p>{{ current.review.stuck }}</p>
          </div>
          <div>
            <strong>下次改进</strong>
            <p>{{ current.review.action }}</p>
          </div>
        </div>

        <el-input v-model="current.markdown" type="textarea" :rows="7" placeholder="Markdown 复盘笔记" />
      </main>
    </section>

    <el-dialog v-model="dialogVisible" title="新增面经" width="520px">
      <el-form label-width="86px">
        <el-form-item label="公司">
          <el-input v-model="draft.company" />
        </el-form-item>
        <el-form-item label="岗位">
          <el-input v-model="draft.role" />
        </el-form-item>
        <el-form-item label="轮次">
          <el-select v-model="draft.round" style="width: 100%">
            <el-option v-for="round in timeline" :key="round" :label="round" :value="round" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addExperience">保存</el-button>
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
const resultMap = { pending: '跟进中', passed: '通过', failed: '已结束' }
const roundFilter = ref('all')
const selectedId = ref('exp_001')
const dialogVisible = ref(false)
const draft = reactive({ company: '小红书', role: '前端实习生', round: '一面' })
const remoteStats = ref(null)

const experiences = reactive([
  {
    id: 'exp_001',
    company: '字节跳动',
    role: '前端实习生',
    city: '上海',
    date: '2026-04-18',
    round: '一面',
    result: 'pending',
    questions: [
      { category: 'Vue', content: 'Vue3 响应式原理是什么？' },
      { category: '项目', content: '你的权限路由是如何设计的？' },
      { category: '网络', content: '缓存策略怎么落地到静态资源？' }
    ],
    review: {
      good: '项目背景和路由权限讲得比较完整。',
      stuck: '网络缓存回答不够细，ETag 优先级说得不稳定。',
      action: '补强强缓存、协商缓存和部署缓存策略。'
    },
    markdown: '### 复盘\n- 响应式原理需要补充 track/trigger。\n- 项目深挖要准备性能优化数据。'
  },
  {
    id: 'exp_002',
    company: '阿里巴巴',
    role: '前端开发实习生',
    city: '杭州',
    date: '2026-04-24',
    round: '二面',
    result: 'passed',
    questions: [
      { category: 'JavaScript', content: '手写 Promise.allSettled。' },
      { category: '算法', content: '最长无重复子串如何优化？' }
    ],
    review: {
      good: '手写题思路清楚，边界条件覆盖得比较完整。',
      stuck: '算法复杂度表达略慢。',
      action: '把滑动窗口模板整理成固定表达。'
    },
    markdown: ''
  },
  {
    id: 'exp_003',
    company: '腾讯',
    role: '前端开发实习生',
    city: '深圳',
    date: '2026-05-02',
    round: 'HR 面',
    result: 'pending',
    questions: [
      { category: '表达', content: '为什么选择前端方向？' },
      { category: '项目', content: 'OfferPilot 后续怎么扩展？' }
    ],
    review: {
      good: '求职动机和项目规划比较自然。',
      stuck: '对团队协作经历举例不够具体。',
      action: '准备一个冲突处理和一个主动推进案例。'
    },
    markdown: ''
  }
])

const filteredExperiences = computed(() => {
  if (roundFilter.value === 'all') return experiences
  return experiences.filter((item) => item.round === roundFilter.value)
})

const current = computed(() => experiences.find((item) => item.id === selectedId.value) || experiences[0])

const stats = computed(() => [
  { label: '面经数量', value: remoteStats.value?.total ?? experiences.length },
  { label: '跟进中', value: remoteStats.value?.pending ?? experiences.filter((item) => item.result === 'pending').length },
  { label: '已通过', value: remoteStats.value?.passed ?? experiences.filter((item) => item.result === 'passed').length }
])

function questionGroups(item) {
  return [...new Set(item.questions.map((question) => question.category))]
}

function resultClass(result) {
  if (result === 'passed') return 'green'
  if (result === 'failed') return 'red'
  return 'orange'
}

function stepIndex(step) {
  return timeline.indexOf(step)
}

async function addExperience() {
  const created = await experienceApi.create({
    company: draft.company,
    role: draft.role,
    city: '远程',
    date: '2026-05-14',
    round: draft.round,
    result: 'pending',
    questions: [{ category: '待整理', content: '记录本轮面试问题' }],
    review: { good: '待补充', stuck: '待补充', action: '待补充' },
    markdown: ''
  })
  experiences.unshift(created)
  selectedId.value = created.id
  dialogVisible.value = false
}

function replaceExperiences(list) {
  if (!Array.isArray(list) || list.length === 0) return
  experiences.splice(0, experiences.length, ...list)
  selectedId.value = list[0].id
}

async function loadExperiences() {
  const result = await experienceApi.getList({
    page: 1,
    pageSize: 100
  })
  const list = result.list || result
  replaceExperiences(list)
  if (Array.isArray(list)) {
    remoteStats.value = {
      total: list.length,
      pending: list.filter((item) => item.result === 'pending').length,
      passed: list.filter((item) => item.result === 'passed').length
    }
  }
}

async function saveExperience(experience) {
  if (!experience?.id) return
  const updated = await experienceApi.update(experience.id, experience)
  Object.assign(experience, updated)
  ElMessage.success('面经已保存')
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
  background: #fff;
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
}
</style>
