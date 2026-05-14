<template>
  <div class="op-page algorithms">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">Algorithm Lab</div>
        <h1 class="op-title">算法练习</h1>
        <p class="op-subtitle">整理实习高频算法题，在同一页面完成题意、思路、代码草稿、测试用例和复盘记录。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="VideoPlay" @click="runCases">运行用例</el-button>
        <el-button :icon="DocumentChecked" @click="markDone">标记完成</el-button>
      </div>
    </section>

    <section class="op-grid cols-3 stats-row">
      <div class="op-stat" v-for="item in stats" :key="item.label">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </div>
    </section>

    <section class="op-grid algorithm-layout">
      <aside class="op-card pad">
        <div class="op-section-title">
          <span>题目列表</span>
          <el-select v-model="filterStatus" style="width: 130px">
            <el-option label="全部" value="all" />
            <el-option label="未开始" value="todo" />
            <el-option label="进行中" value="doing" />
            <el-option label="已完成" value="done" />
          </el-select>
        </div>
        <div class="op-list">
          <article
            v-for="problem in filteredProblems"
            :key="problem.id"
            class="op-list-item"
            :class="{ active: problem.id === selectedId }"
            @click="selectedId = problem.id"
          >
            <div class="op-row">
              <strong>{{ problem.id }} {{ problem.title }}</strong>
              <span class="op-tag" :class="difficultyClass(problem.difficulty)">{{ difficultyMap[problem.difficulty] }}</span>
            </div>
            <div class="op-tags">
              <span v-for="tag in problem.tags" :key="tag" class="op-tag">{{ tag }}</span>
              <span class="op-tag green" v-if="problem.status === 'done'">已完成</span>
              <span class="op-tag orange" v-else-if="problem.status === 'doing'">进行中</span>
              <span class="op-tag red" v-else>未开始</span>
            </div>
          </article>
        </div>
      </aside>

      <main class="op-card pad op-detail">
        <div class="op-section-title">
          <span>题目详情</span>
          <el-link :href="currentProblem.leetcodeUrl" target="_blank" type="primary">LeetCode</el-link>
        </div>
        <h3>{{ currentProblem.title }}</h3>
        <p>{{ currentProblem.description }}</p>

        <el-tabs v-model="activeTab" class="workspace-tabs">
          <el-tab-pane label="思路模板" name="idea">
            <div class="note-box">
              <strong>解题思路</strong>
              <p>{{ currentProblem.idea }}</p>
              <strong>复杂度</strong>
              <p>{{ currentProblem.complexity }}</p>
            </div>
          </el-tab-pane>
          <el-tab-pane label="代码草稿" name="code">
            <el-input
              v-model="currentProblem.codeDraft"
              type="textarea"
              :rows="14"
              spellcheck="false"
              class="code-editor"
              @blur="saveCodeDraft"
            />
          </el-tab-pane>
          <el-tab-pane label="测试用例" name="cases">
            <div class="case-list">
              <div v-for="test in currentProblem.testCases" :key="test.input" class="case-item">
                <div>
                  <span class="op-muted">输入</span>
                  <code>{{ test.input }}</code>
                </div>
                <div>
                  <span class="op-muted">期望</span>
                  <code>{{ test.expected }}</code>
                </div>
                <div>
                  <span class="op-muted">结果</span>
                  <span class="op-tag" :class="runStatusClass">{{ runStatusText }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="复盘" name="review">
            <el-input v-model="currentProblem.notes" type="textarea" :rows="8" placeholder="记录错因、二刷日期和优化点" @blur="saveProblem" />
          </el-tab-pane>
        </el-tabs>
      </main>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { DocumentChecked, VideoPlay } from '@element-plus/icons-vue'
import { algorithmApi } from '@/api/front'

const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }
const activeTab = ref('idea')
const filterStatus = ref('all')
const selectedId = ref('lc_003')
const runStatus = ref('idle')
const remoteStats = ref(null)

const problems = reactive([
  {
    id: 'lc_003',
    title: '无重复字符的最长子串',
    leetcodeUrl: 'https://leetcode.cn/problems/longest-substring-without-repeating-characters/',
    difficulty: 'medium',
    tags: ['sliding-window', 'hash-map'],
    status: 'doing',
    description: '给定一个字符串，找出其中不含重复字符的最长子串长度。',
    idea: '使用滑动窗口维护当前无重复区间，右指针扩展，遇到重复字符时移动左指针到重复字符后一位。',
    complexity: '时间复杂度 O(n)，空间复杂度 O(k)，k 为字符集大小。',
    codeDraft: 'function lengthOfLongestSubstring(s) {\n  const map = new Map()\n  let left = 0\n  let ans = 0\n\n  for (let right = 0; right < s.length; right++) {\n    const char = s[right]\n    if (map.has(char) && map.get(char) >= left) {\n      left = map.get(char) + 1\n    }\n    map.set(char, right)\n    ans = Math.max(ans, right - left + 1)\n  }\n\n  return ans\n}',
    notes: '注意 left 只能向右移动，不能回退。',
    testCases: [{ input: '"abcabcbb"', expected: 3 }]
  },
  {
    id: 'lc_020',
    title: '有效的括号',
    leetcodeUrl: 'https://leetcode.cn/problems/valid-parentheses/',
    difficulty: 'easy',
    tags: ['stack'],
    status: 'done',
    description: '判断只包含括号的字符串是否有效闭合。',
    idea: '遇到左括号入栈，遇到右括号时检查栈顶是否匹配。',
    complexity: '时间复杂度 O(n)，空间复杂度 O(n)。',
    codeDraft: 'function isValid(s) {\n  const stack = []\n  const pairs = { ")": "(", "]": "[", "}": "{" }\n  for (const char of s) {\n    if (!pairs[char]) stack.push(char)\n    else if (stack.pop() !== pairs[char]) return false\n  }\n  return stack.length === 0\n}',
    notes: '边界：空栈遇到右括号直接 false。',
    testCases: [{ input: '"()[]{}"', expected: true }]
  },
  {
    id: 'lc_146',
    title: 'LRU 缓存',
    leetcodeUrl: 'https://leetcode.cn/problems/lru-cache/',
    difficulty: 'hard',
    tags: ['linked-list', 'hash-map'],
    status: 'todo',
    description: '设计一个支持 O(1) get 和 put 的 LRU 缓存。',
    idea: 'Map 快速定位节点，双向链表维护最近使用顺序。',
    complexity: 'get/put 时间复杂度 O(1)，空间复杂度 O(capacity)。',
    codeDraft: '// TODO: Map + 双向链表',
    notes: '',
    testCases: [{ input: '["LRUCache","put","get"]', expected: '[null,null,1]' }]
  }
])

const filteredProblems = computed(() => {
  if (filterStatus.value === 'all') return problems
  return problems.filter((item) => item.status === filterStatus.value)
})

const currentProblem = computed(() => problems.find((item) => item.id === selectedId.value) || problems[0])

const stats = computed(() => [
  { label: '题目总数', value: remoteStats.value?.total ?? problems.length },
  {
    label: '完成率',
    value: remoteStats.value?.completionRate ? `${remoteStats.value.completionRate}%` : `${Math.round((problems.filter((item) => item.status === 'done').length / problems.length) * 100)}%`
  },
  { label: '本周复盘', value: remoteStats.value?.reviewCountThisWeek ?? problems.filter((item) => item.notes).length }
])

const runStatusText = computed(() => {
  if (runStatus.value === 'running') return '运行中'
  if (runStatus.value === 'passed') return '通过'
  return '待运行'
})

const runStatusClass = computed(() => {
  if (runStatus.value === 'passed') return 'green'
  if (runStatus.value === 'running') return 'orange'
  return ''
})

function difficultyClass(difficulty) {
  if (difficulty === 'easy') return 'green'
  if (difficulty === 'hard') return 'red'
  return 'orange'
}

async function runCases() {
  runStatus.value = 'running'
  currentProblem.value.status = 'doing'
  try {
    const result = await algorithmApi.runCases(currentProblem.value.id, {
      code: currentProblem.value.codeDraft,
      testCases: currentProblem.value.testCases
    })
    runStatus.value = result.status === 'failed' ? 'idle' : 'passed'
  } catch {
    runStatus.value = 'idle'
  }
}

async function markDone() {
  currentProblem.value.status = 'done'
  await algorithmApi.update(currentProblem.value.id, { status: 'done' })
  await loadStats()
}

async function saveCodeDraft() {
  await algorithmApi.saveCodeDraft(currentProblem.value.id, {
    codeDraft: currentProblem.value.codeDraft
  })
}

async function saveProblem() {
  await algorithmApi.update(currentProblem.value.id, {
    notes: currentProblem.value.notes,
    status: currentProblem.value.status
  })
}

function replaceProblems(list) {
  if (!Array.isArray(list) || list.length === 0) return
  problems.splice(0, problems.length, ...list)
  selectedId.value = list[0].id
}

async function loadProblems() {
  const result = await algorithmApi.getList({
    page: 1,
    pageSize: 100
  })
  replaceProblems(result.list || result)
}

async function loadStats() {
  remoteStats.value = await algorithmApi.getStats()
}

onMounted(async () => {
  await Promise.all([loadProblems(), loadStats()])
})
</script>

<style src="./workbench.css"></style>
<style scoped>
.stats-row {
  margin-bottom: 16px;
}

.algorithm-layout {
  grid-template-columns: 360px minmax(0, 1fr);
}

.workspace-tabs {
  margin-top: 18px;
}

.note-box {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: 8px;
  background: #f8fafc;
}

.code-editor :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  line-height: 1.6;
}

.case-list {
  display: grid;
  gap: 12px;
}

.case-item {
  display: grid;
  grid-template-columns: 1fr 1fr 120px;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.case-item > div {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (max-width: 1100px) {
  .algorithm-layout,
  .case-item {
    grid-template-columns: 1fr;
  }
}
</style>
