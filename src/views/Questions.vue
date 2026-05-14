<template>
  <div class="op-page questions">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">Question Bank</div>
        <h1 class="op-title">面试题库</h1>
        <p class="op-subtitle">按 CSS、JavaScript、Vue、网络和算法分类管理高频题，支持搜索、筛选、收藏和掌握状态。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Star">收藏优先</el-button>
        <el-button :icon="Refresh">复习计划</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid cols-2 main-grid">
      <div class="op-card pad">
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

        <div class="op-list question-list">
          <article
            v-for="question in filteredQuestions"
            :key="question.id"
            class="op-list-item"
            :class="{ active: question.id === selectedQuestion.id }"
            @click="selectedId = question.id"
          >
            <div class="op-row">
              <strong>{{ question.title }}</strong>
              <el-button link :icon="question.starred ? StarFilled : Star" @click.stop="toggleStar(question)" />
            </div>
            <div class="op-tags">
              <span class="op-tag">{{ question.category }}</span>
              <span class="op-tag orange">{{ difficultyMap[question.difficulty] }}</span>
              <span class="op-tag green" v-if="question.mastered">已掌握</span>
              <span class="op-tag red" v-else>待复习</span>
            </div>
            <p class="last-review">上次复习：{{ question.lastReviewedAt }}</p>
          </article>
        </div>
      </div>

      <aside class="op-card pad op-detail">
        <div class="op-section-title">
          <span>题目详情</span>
          <el-switch
            v-model="selectedQuestion.mastered"
            active-text="已掌握"
            inactive-text="待复习"
            @change="updateMastery(selectedQuestion)"
          />
        </div>
        <h3>{{ selectedQuestion.title }}</h3>
        <p>{{ selectedQuestion.answer }}</p>

        <div class="detail-block">
          <strong>追问</strong>
          <ul>
            <li v-for="item in selectedQuestion.followUps" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="detail-block">
          <strong>易错点</strong>
          <ul>
            <li v-for="item in selectedQuestion.pitfalls" :key="item">{{ item }}</li>
          </ul>
        </div>
        <el-input
          v-model="selectedQuestion.note"
          type="textarea"
          :rows="5"
          placeholder="写下自己的补充笔记"
          @blur="saveNote(selectedQuestion)"
        />
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Refresh, Search, Star, StarFilled } from '@element-plus/icons-vue'
import { questionApi } from '@/api/front'

const categories = ['全部', 'CSS', 'JavaScript', 'Vue', 'Network', 'Algorithm']
const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }

const questions = reactive([
  {
    id: 'q_css_001',
    title: 'Flex 和 Grid 的使用场景有什么区别？',
    category: 'CSS',
    difficulty: 'easy',
    tags: ['layout', 'grid', 'flex'],
    answer: 'Flex 更适合一维排布，Grid 更适合二维布局。工作台、看板这类横纵都需要控制的区域更适合 Grid。',
    followUps: ['flex: 1 的含义是什么？', 'Grid 如何实现响应式列？'],
    pitfalls: ['不要把 Grid 只理解成表格布局。'],
    mastered: true,
    starred: false,
    lastReviewedAt: '2026-05-12',
    note: ''
  },
  {
    id: 'q_js_001',
    title: '介绍一下事件循环',
    category: 'JavaScript',
    difficulty: 'medium',
    tags: ['event-loop', 'promise', 'async'],
    answer: '同步任务先进入调用栈，异步回调分别进入宏任务或微任务队列。每轮宏任务结束后会清空当前微任务队列，再进入渲染和下一轮任务。',
    followUps: ['Promise.then 属于什么任务？', 'setTimeout 和 requestAnimationFrame 的时机区别？'],
    pitfalls: ['不要把 async 函数本身说成微任务。'],
    mastered: false,
    starred: true,
    lastReviewedAt: '2026-05-13',
    note: '结合页面渲染时机再复盘一次。'
  },
  {
    id: 'q_vue_001',
    title: 'Vue3 响应式原理是什么？',
    category: 'Vue',
    difficulty: 'medium',
    tags: ['proxy', 'reactivity', 'effect'],
    answer: 'Vue3 使用 Proxy 拦截对象读写，在 get 时收集依赖，在 set 时触发对应 effect 重新执行，从而驱动视图更新。',
    followUps: ['ref 和 reactive 的区别？', 'computed 为什么有缓存？'],
    pitfalls: ['不要忽略依赖收集和触发更新是两个阶段。'],
    mastered: false,
    starred: true,
    lastReviewedAt: '2026-05-11',
    note: ''
  },
  {
    id: 'q_net_001',
    title: '强缓存和协商缓存怎么判断？',
    category: 'Network',
    difficulty: 'hard',
    tags: ['cache', 'http'],
    answer: '强缓存通过 Cache-Control 或 Expires 判断是否直接使用缓存；协商缓存会携带 ETag 或 Last-Modified 与服务端确认资源是否变化。',
    followUps: ['ETag 和 Last-Modified 谁优先？', 'no-cache 和 no-store 的区别？'],
    pitfalls: ['no-cache 不是不缓存，而是使用前需要协商。'],
    mastered: false,
    starred: false,
    lastReviewedAt: '2026-05-10',
    note: ''
  }
])

const keyword = ref('')
const difficulty = ref('all')
const currentCategory = ref('全部')
const onlyStarred = ref(false)
const onlyUnmastered = ref(false)
const selectedId = ref(questions[1].id)
const remoteStats = ref(null)

const filteredQuestions = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  return questions.filter((item) => {
    const hitKeyword = !text || [item.title, item.answer, ...item.tags].join(' ').toLowerCase().includes(text)
    const hitCategory = currentCategory.value === '全部' || item.category === currentCategory.value
    const hitDifficulty = difficulty.value === 'all' || item.difficulty === difficulty.value
    const hitStarred = !onlyStarred.value || item.starred
    const hitMastered = !onlyUnmastered.value || !item.mastered
    return hitKeyword && hitCategory && hitDifficulty && hitStarred && hitMastered
  })
})

const selectedQuestion = computed(() => {
  return questions.find((item) => item.id === selectedId.value) || filteredQuestions.value[0] || questions[0]
})

const stats = computed(() => [
  { label: '题库总量', value: remoteStats.value?.total ?? questions.length },
  { label: '收藏题目', value: remoteStats.value?.starred ?? questions.filter((item) => item.starred).length },
  { label: '待复习', value: remoteStats.value?.reviewTodo ?? questions.filter((item) => !item.mastered).length }
])

function replaceQuestions(list) {
  if (!Array.isArray(list) || list.length === 0) return
  questions.splice(0, questions.length, ...list)
  selectedId.value = list[0].id
}

async function loadQuestions() {
  const result = await questionApi.getList({
    page: 1,
    pageSize: 100
  })
  replaceQuestions(result.list || result)
}

async function loadStats() {
  remoteStats.value = await questionApi.getStats()
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

onMounted(async () => {
  await Promise.all([loadQuestions(), loadStats()])
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
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
  max-height: 560px;
  overflow: auto;
}

.last-review {
  margin-top: 10px;
  color: #667085;
  font-size: 13px;
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
</style>
