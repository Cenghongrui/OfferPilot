<template>
  <div class="op-page mock-interview">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">Mock Interview</div>
        <h1 class="op-title">模拟面试</h1>
        <p class="op-subtitle">选择专项模式后随机抽题，按真实节奏计时作答、评分，并生成复盘报告。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="VideoPlay" @click="startInterview">开始模拟</el-button>
        <el-button :icon="Refresh" @click="resetInterview">重置</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid mock-layout">
      <aside class="op-card pad">
        <div class="op-section-title">
          <span>模式选择</span>
          <span class="op-tag" :class="stateClass">{{ stateText }}</span>
        </div>
        <div class="mode-list">
          <button
            v-for="mode in modes"
            :key="mode.name"
            :class="{ active: activeMode.name === mode.name }"
            @click="activeMode = mode"
          >
            <strong>{{ mode.name }}</strong>
            <span>{{ mode.desc }}</span>
          </button>
        </div>

        <div class="timer-panel">
          <span>当前题用时</span>
          <strong>{{ formatTime(questionSeconds) }}</strong>
          <span>总用时</span>
          <strong>{{ formatTime(totalSeconds) }}</strong>
        </div>
      </aside>

      <main class="op-card pad op-detail">
        <div class="op-section-title">
          <span>抽题面板</span>
          <div>
            <el-button size="small" :icon="Switch" @click="nextQuestion">换一题</el-button>
            <el-button size="small" :icon="Finished" type="primary" @click="finishInterview">生成报告</el-button>
          </div>
        </div>

        <div class="question-panel">
          <span class="op-tag orange">{{ activeMode.name }}</span>
          <h3>{{ currentQuestion.title }}</h3>
          <p>{{ currentQuestion.prompt }}</p>
          <div class="follow-ups">
            <strong>追问</strong>
            <ul>
              <li v-for="item in currentQuestion.followUps" :key="item">{{ item }}</li>
            </ul>
          </div>
          <el-alert :title="currentQuestion.hint" type="info" :closable="false" />
        </div>

        <div class="answer-grid">
          <div>
            <div class="op-section-title small-title">
              <span>作答笔记</span>
            </div>
            <el-input v-model="answerNote" type="textarea" :rows="8" placeholder="记录自己的回答大纲、案例和卡点" />
          </div>
          <div>
            <div class="op-section-title small-title">
              <span>评分表</span>
            </div>
            <div class="score-list">
              <label v-for="item in scoreItems" :key="item.key">
                <span>{{ item.label }}</span>
                <el-rate v-model="scores[item.key]" :max="5" />
              </label>
            </div>
          </div>
        </div>
      </main>

      <aside class="op-card pad report-card">
        <div class="op-section-title">
          <span>面试报告</span>
        </div>
        <template v-if="report">
          <div class="report-score">
            <strong>{{ report.total }}</strong>
            <span>综合得分</span>
          </div>
          <div class="report-block">
            <strong>本次问题</strong>
            <p>{{ report.question }}</p>
          </div>
          <div class="report-block">
            <strong>薄弱点</strong>
            <p>{{ report.weakness }}</p>
          </div>
          <div class="report-block">
            <strong>复习建议</strong>
            <p>{{ report.suggestion }}</p>
          </div>
        </template>
        <el-empty v-else description="完成评分后生成报告" />
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { Finished, Refresh, Switch, VideoPlay } from '@element-plus/icons-vue'
import { mockInterviewApi } from '@/api/front'

const modes = [
  { name: '基础八股', desc: 'CSS / JS / 浏览器基础' },
  { name: 'Vue 专项', desc: '响应式、组件通信、Router' },
  { name: '网络专项', desc: '缓存、跨域、HTTP' },
  { name: '项目深挖', desc: '架构、性能、难点复盘' },
  { name: '算法快问', desc: '数组、栈、滑动窗口' }
]

const questionPool = [
  {
    mode: 'Vue 专项',
    title: 'Vue3 响应式原理是什么？',
    prompt: '请从 Proxy、依赖收集、触发更新和视图渲染四个层次讲清楚。',
    followUps: ['ref 和 reactive 的区别？', 'computed 为什么有缓存？'],
    hint: '提示：可以按 get 收集、set 触发、effect 重新执行来组织。'
  },
  {
    mode: '网络专项',
    title: '浏览器缓存策略如何设计？',
    prompt: '请说明强缓存、协商缓存，以及前端静态资源部署时如何避免缓存问题。',
    followUps: ['no-cache 和 no-store 区别？', 'hash 文件名解决了什么？'],
    hint: '提示：回答里最好带上 Cache-Control、ETag 和构建产物 hash。'
  },
  {
    mode: '项目深挖',
    title: 'OfferPilot 的数据层如何扩展到后端接口？',
    prompt: '请说明本地 mock、localStorage、后端 API 之间如何解耦。',
    followUps: ['如何处理 loading 和 error？', '如何做乐观更新？'],
    hint: '提示：强调页面组件不直接关心存储细节。'
  },
  {
    mode: '算法快问',
    title: '无重复字符的最长子串怎么做？',
    prompt: '请讲出滑动窗口的边界移动规则，并说明复杂度。',
    followUps: ['left 为什么不能回退？', 'Map 里存字符还是下标？'],
    hint: '提示：用 right 扩展窗口，重复时更新 left。'
  },
  {
    mode: '基础八股',
    title: '事件循环中宏任务和微任务的执行顺序？',
    prompt: '请结合 Promise、setTimeout 和页面渲染时机说明。',
    followUps: ['async/await 如何拆解？', 'MutationObserver 属于什么任务？'],
    hint: '提示：每轮宏任务结束后会清空微任务队列。'
  }
]

const scoreItems = [
  { key: 'accuracy', label: '准确性' },
  { key: 'completeness', label: '完整性' },
  { key: 'expression', label: '表达清晰度' },
  { key: 'projectLink', label: '项目结合度' }
]

const activeMode = ref(modes[1])
const currentQuestion = ref(questionPool[0])
const state = ref('idle')
const totalSeconds = ref(0)
const questionSeconds = ref(0)
const answerNote = ref('')
const report = ref(null)
const sessionId = ref('')
const remoteStats = ref(null)
const scores = reactive({ accuracy: 3, completeness: 3, expression: 3, projectLink: 3 })
let timer = null

const stateText = computed(() => {
  const map = { idle: '未开始', running: '进行中', paused: '已暂停', finished: '已完成' }
  return map[state.value]
})

const stateClass = computed(() => {
  if (state.value === 'running') return 'green'
  if (state.value === 'finished') return ''
  return 'orange'
})

const stats = computed(() => [
  { label: '模式数量', value: remoteStats.value?.modeCount ?? modes.length },
  { label: '已用时', value: formatTime(totalSeconds.value || remoteStats.value?.totalDuration || 0) },
  { label: '平均评分', value: remoteStats.value?.averageScore ?? averageScore.value }
])

const averageScore = computed(() => {
  const values = Object.values(scores)
  return (values.reduce((sum, item) => sum + item, 0) / values.length).toFixed(1)
})

async function startInterview() {
  state.value = 'running'
  report.value = null
  await pickQuestion()
  const session = await mockInterviewApi.createSession({
    mode: activeMode.value.name,
    questionIds: [currentQuestion.value.id].filter(Boolean)
  })
  sessionId.value = session.id
  startTimer()
}

function startTimer() {
  window.clearInterval(timer)
  timer = window.setInterval(() => {
    totalSeconds.value += 1
    questionSeconds.value += 1
  }, 1000)
}

async function pickQuestion() {
  try {
    currentQuestion.value = await mockInterviewApi.getRandomQuestion({
      mode: activeMode.value.name
    })
  } catch {
    const scoped = questionPool.filter((item) => item.mode === activeMode.value.name)
    const source = scoped.length ? scoped : questionPool
    currentQuestion.value = source[Math.floor(Math.random() * source.length)]
  }
  questionSeconds.value = 0
  answerNote.value = ''
}

async function nextQuestion() {
  await pickQuestion()
  if (state.value === 'idle') state.value = 'running'
  startTimer()
}

async function finishInterview() {
  state.value = 'finished'
  window.clearInterval(timer)
  if (sessionId.value) {
    report.value = await mockInterviewApi.generateReport(sessionId.value, {
      questionId: currentQuestion.value.id,
      answerNote: answerNote.value,
      scores,
      duration: totalSeconds.value
    })
  } else {
    const total = Object.values(scores).reduce((sum, item) => sum + item, 0)
    report.value = {
      total,
      question: currentQuestion.value.title,
      weakness: scores.completeness < 4 ? '回答结构还可以更完整，追问需要提前准备例子。' : '整体稳定，继续补充项目结合案例。',
      suggestion: `复习 ${activeMode.value.name} 的核心概念，并把本次作答笔记沉淀进面经。`
    }
  }
  await loadStats()
}

function resetInterview() {
  window.clearInterval(timer)
  state.value = 'idle'
  totalSeconds.value = 0
  questionSeconds.value = 0
  answerNote.value = ''
  report.value = null
  sessionId.value = ''
  Object.assign(scores, { accuracy: 3, completeness: 3, expression: 3, projectLink: 3 })
}

function formatTime(seconds) {
  const min = String(Math.floor(seconds / 60)).padStart(2, '0')
  const sec = String(seconds % 60).padStart(2, '0')
  return `${min}:${sec}`
}

onBeforeUnmount(() => {
  window.clearInterval(timer)
})

async function loadModes() {
  const list = await mockInterviewApi.getModes()
  if (Array.isArray(list) && list.length) {
    modes.splice(0, modes.length, ...list)
    activeMode.value = modes[0]
  }
}

async function loadStats() {
  remoteStats.value = await mockInterviewApi.getStats()
}

onMounted(async () => {
  await Promise.all([loadModes(), loadStats()])
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.mock-layout {
  grid-template-columns: 300px minmax(0, 1fr) 300px;
}

.mode-list {
  display: grid;
  gap: 10px;
}

.mode-list button {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #172033;
  text-align: left;
  background: #fff;
  cursor: pointer;
}

.mode-list button span {
  color: #667085;
  font-size: 13px;
}

.mode-list button.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.timer-panel {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-top: 18px;
  padding: 16px;
  border-radius: 8px;
  background: #172033;
}

.timer-panel span {
  color: #cbd5e1;
  font-size: 13px;
}

.timer-panel strong {
  color: #fff;
  font-size: 26px;
}

.question-panel {
  display: grid;
  gap: 12px;
  padding: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.follow-ups ul {
  margin: 8px 0 0;
  padding-left: 18px;
  color: #475467;
  line-height: 1.8;
}

.answer-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 16px;
  margin-top: 16px;
}

.small-title {
  margin-bottom: 10px;
}

.score-list {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.score-list label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 130px;
  margin-bottom: 16px;
  border-radius: 8px;
  color: #fff;
  background: #2563eb;
}

.report-score strong {
  font-size: 42px;
  line-height: 1;
}

.report-block {
  padding: 14px 0;
  border-top: 1px solid #e5e7eb;
}

.report-block strong {
  display: block;
  margin-bottom: 8px;
}

@media (max-width: 1200px) {
  .mock-layout,
  .answer-grid {
    grid-template-columns: 1fr;
  }
}
</style>
