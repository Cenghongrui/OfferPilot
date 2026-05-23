<template>
  <div class="op-page mock-interview-v2">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">AI 模拟面试</div>
        <h1 class="op-title">模拟面试</h1>
        <p class="op-subtitle">AI 面试官按岗位和技术栈逐题提问，支持追问与流式对话，结束后生成多维度中文复盘报告。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="VideoPlay" @click="showStartDialog = true">开始面试</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>
    </section>

    <section class="mock-layout-v2">
      <!-- 左侧：历史面试列表 -->
      <aside class="op-card pad history-panel">
        <InterviewHistory
          :sessions="sessions"
          :current-session-id="sessionId"
          :loading="sessionsLoading"
          @select="handleResumeSession"
          @start="showStartDialog = true"
        />
      </aside>

      <!-- 右侧：面试主区域 -->
      <div class="interview-main">
        <div class="chat-area" ref="chatContainerRef">
          <InterviewChat
            ref="chatRef"
            :messages="messages"
            :streaming-content="streamingContent"
            :current-question-number="currentQuestionNumber"
          />
        </div>
        <div class="outline-area">
          <InterviewOutline
            :questions="outlineQuestions"
            :active-question="currentQuestionNumber"
            @detail="handleShowQuestionDetail"
          />
        </div>
        <div class="input-area">
          <ChatInput
            :disabled="status !== 'running'"
            :loading="chatLoading"
            @send="handleSendMessage"
            @next="handleNextQuestion"
            @end="handleEndInterview"
          />
        </div>
      </div>
    </section>

    <StartInterviewDialog
      :visible="showStartDialog"
      :loading="startLoading"
      :modes="modes"
      @confirm="handleStartInterview"
      @cancel="showStartDialog = false"
    />

    <ReportModal
      :visible="showReportModal"
      :report="report"
      :session-id="sessionId"
      @continue="handleContinueInterview"
      @close="showReportModal = false"
    />

    <QuestionDetailDialog
      :visible="showQuestionDetail"
      :question-number="detailQuestionNumber"
      :messages="messages"
      :current-question-number="currentQuestionNumber"
      :streaming-content="streamingContent"
      @close="showQuestionDetail = false"
    />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Refresh } from '@element-plus/icons-vue'
import { mockInterviewApi } from '@/api/front'
import ChatInput from '@/components/mock-interview/ChatInput.vue'
import InterviewOutline from '@/components/mock-interview/InterviewOutline.vue'
import InterviewChat from '@/components/mock-interview/InterviewChat.vue'
import InterviewHistory from '@/components/mock-interview/InterviewHistory.vue'
import StartInterviewDialog from '@/components/mock-interview/StartInterviewDialog.vue'
import ReportModal from '@/components/mock-interview/ReportModal.vue'
import QuestionDetailDialog from '@/components/mock-interview/QuestionDetailDialog.vue'

// ——— 面试配置 ———
const modes = ref([
  { name: '前端基础面', desc: 'CSS、JavaScript、浏览器基础' },
  { name: 'Vue 专项面', desc: '响应式、组件通信、路由和状态管理' },
  { name: '网络与工程化', desc: 'HTTP、缓存、跨域、构建和部署' },
  { name: '项目深挖面', desc: '项目边界、接口设计、性能和难点复盘' },
  { name: '算法快问', desc: '数组、栈、哈希表、滑动窗口' }
])

// ——— 会话状态 ———
const sessionId = ref('')
const status = ref('idle')
const messages = ref([])
const questionCount = ref(0)
const currentQuestionNumber = ref(1)

// ——— UI 状态 ———
const sessions = ref([])
const sessionsLoading = ref(false)
const chatLoading = ref(false)
const streamingContent = ref('')
const report = ref(null)
const showReportModal = ref(false)
const showStartDialog = ref(false)
const showQuestionDetail = ref(false)
const detailQuestionNumber = ref(0)
const startLoading = ref(false)

// ——— 计时 ———
const totalSeconds = ref(0)
let timer = null

// ——— Refs ———
const chatRef = ref(null)
const chatContainerRef = ref(null)

// ——— 工具方法 ———
const QUESTION_PREFIX_RE = /^第(\d+)题[：:]\s*/

function parseQuestionNumber(content) {
  const match = content?.match(QUESTION_PREFIX_RE)
  return match ? parseInt(match[1], 10) : null
}

function annotateMessages(raw) {
  if (!Array.isArray(raw)) return []
  let currentQ = 0
  return raw.map((msg) => {
    const qNum = parseQuestionNumber(msg.content)
    if (qNum) currentQ = qNum
    return { ...msg, questionNumber: msg.questionNumber || (qNum ? qNum : 0) }
  })
}

// ——— 计算属性 ———
const outlineQuestions = computed(() => {
  const seen = new Map()
  for (const msg of messages.value) {
    if (msg.questionNumber && !seen.has(msg.questionNumber)) {
      const label = msg.content.replace(QUESTION_PREFIX_RE, '')
      const shortLabel = label.length > 30 ? label.slice(0, 30) + '...' : label
      seen.set(msg.questionNumber, { number: msg.questionNumber, label: shortLabel })
    }
  }
  return Array.from(seen.values())
})

// ——— 计时器 ———
function startTimer() {
  stopTimer()
  timer = window.setInterval(() => { totalSeconds.value += 1 }, 1000)
}

function stopTimer() {
  if (timer) {
    window.clearInterval(timer)
    timer = null
  }
}

function formatTime(seconds) {
  const min = String(Math.floor((seconds || 0) / 60)).padStart(2, '0')
  const sec = String((seconds || 0) % 60).padStart(2, '0')
  return `${min}:${sec}`
}

// ——— 加载数据 ———
async function loadSessions() {
  sessionsLoading.value = true
  try {
    const data = await mockInterviewApi.getSessions()
    sessions.value = data?.list || []
  } catch {
    sessions.value = []
  } finally {
    sessionsLoading.value = false
  }
}

async function loadModes() {
  try {
    const list = await mockInterviewApi.getModes()
    if (Array.isArray(list) && list.length) {
      modes.value = list
    }
  } catch { /* use defaults */ }
}

// ——— 面试流程 ———
async function handleStartInterview(formData) {
  startLoading.value = true
  try {
    resetState()
    status.value = 'running'
    startTimer()

    const session = await mockInterviewApi.createSession({
      position: formData.position,
      techStack: formData.techStack,
      interviewType: formData.interviewType,
      mode: formData.interviewType,
      startedAt: new Date().toISOString()
    })
    sessionId.value = session.id

    // 获取第一题
    const qst = await mockInterviewApi.nextQuestion(sessionId.value)
    questionCount.value = qst.number || 1
    currentQuestionNumber.value = qst.number || 1
    messages.value.push({
      role: 'assistant',
      content: qst.question,
      questionNumber: qst.number || 1
    })

    showStartDialog.value = false
    await loadSessions()
  } catch (e) {
    ElMessage.error('开始面试失败，请检查后端服务')
    resetState()
  } finally {
    startLoading.value = false
  }
}

async function handleResumeSession(id) {
  if (id === sessionId.value) return
  try {
    stopTimer()
    const session = await mockInterviewApi.getSession(id)
    sessionId.value = id
    messages.value = annotateMessages(session.messages || [])
    questionCount.value = session.questionCount || 0
    currentQuestionNumber.value = session.questionCount || 1
    status.value = session.status || 'finished'
    report.value = session.report || null

    if (session.status === 'finished' && session.report) {
      showReportModal.value = true
    } else if (session.status === 'running') {
      startTimer()
    }
  } catch {
    ElMessage.error('加载面试记录失败')
  }
}

async function handleSendMessage(text) {
  if (!sessionId.value || status.value !== 'running') return

  messages.value.push({ role: 'user', content: text })
  chatLoading.value = true
  streamingContent.value = ''

  try {
    const response = await mockInterviewApi.chat(sessionId.value, text)
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const payload = line.slice(6)
          if (payload === '[DONE]') continue
          try {
            const parsed = JSON.parse(payload)
            if (parsed.token) streamingContent.value += parsed.token
            if (parsed.error) {
              ElMessage.error(parsed.error)
              streamingContent.value = ''
            }
          } catch { /* ignore parse errors */ }
        }
      }
    }
  } catch {
    ElMessage.error('对话请求失败')
  } finally {
    chatLoading.value = false
    if (streamingContent.value) {
      messages.value.push({ role: 'assistant', content: streamingContent.value })
      streamingContent.value = ''
    }
  }
}

async function handleNextQuestion() {
  if (!sessionId.value || status.value !== 'running') return
  chatLoading.value = true
  try {
    const qst = await mockInterviewApi.nextQuestion(sessionId.value)
    questionCount.value = qst.number
    currentQuestionNumber.value = qst.number
    messages.value.push({
      role: 'assistant',
      content: qst.question,
      questionNumber: qst.number
    })
  } catch {
    ElMessage.error('获取题目失败')
  } finally {
    chatLoading.value = false
  }
}

async function handleEndInterview() {
  if (!sessionId.value || status.value !== 'running') {
    ElMessage.warning('请先开始一场面试')
    return
  }
  chatLoading.value = true
  stopTimer()
  try {
    const result = await mockInterviewApi.endSession(sessionId.value)
    status.value = 'finished'
    report.value = { ...result, source: result.source || 'deepseek' }
    showReportModal.value = true
    // 更新会话耗时
    await mockInterviewApi.updateSession(sessionId.value, { duration: totalSeconds.value })
    await loadSessions()
  } catch {
    ElMessage.error('生成报告失败')
  } finally {
    chatLoading.value = false
  }
}

async function handleContinueInterview() {
  if (!sessionId.value) return
  try {
    await mockInterviewApi.updateSession(sessionId.value, { status: 'running' })
    status.value = 'running'
    showReportModal.value = false
    report.value = null
    startTimer()
  } catch {
    ElMessage.error('恢复面试失败')
  }
}

function handleShowQuestionDetail(number) {
  detailQuestionNumber.value = number
  showQuestionDetail.value = true
}

function jumpToQuestion(number) {
  currentQuestionNumber.value = number
  const el = document.getElementById(`question-${number}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function handleReset() {
  stopTimer()
  resetState()
}

function resetState() {
  stopTimer()
  sessionId.value = ''
  status.value = 'idle'
  messages.value = []
  questionCount.value = 0
  currentQuestionNumber.value = 1
  streamingContent.value = ''
  report.value = null
  showReportModal.value = false
  showQuestionDetail.value = false
  detailQuestionNumber.value = 0
  totalSeconds.value = 0
}

onMounted(async () => {
  await Promise.all([loadModes(), loadSessions()])
})

onBeforeUnmount(() => {
  stopTimer()
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.mock-layout-v2 {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 16px;
  height: calc(100vh - 220px);
  min-height: 520px;
}

.history-panel {
  overflow-y: auto;
}

.interview-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  grid-template-rows: 1fr auto;
  gap: 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.chat-area {
  grid-column: 1;
  grid-row: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.outline-area {
  grid-column: 2;
  grid-row: 1;
  border-left: 1px solid #e5e7eb;
  overflow-y: auto;
  background: #fafbfc;
}

.input-area {
  grid-column: 1 / -1;
  grid-row: 2;
  border-top: 1px solid #e5e7eb;
  padding: 12px 16px;
  background: #fff;
}

@media (max-width: 1100px) {
  .mock-layout-v2 {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 0;
  }
  .interview-main {
    grid-template-columns: 1fr;
  }
  .outline-area {
    display: none;
  }
}
</style>
