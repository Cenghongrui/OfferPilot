# OfferPilot 前端实习训练工作台项目文档

## 1. 项目定位

OfferPilot 是一个面向前端实习求职的训练工作台，帮助用户管理面试题、算法题、面经、投递进度和模拟面试记录。

这个项目适合用 Vue3 + JavaScript 手写练习，因为它不是简单 CRUD，而是能自然覆盖前端面试常问能力：

- CSS：复杂布局、响应式、Flex/Grid、卡片列表、看板拖拽、弹窗和抽屉。
- JavaScript：防抖、节流、深拷贝、数组转树、Promise 并发、事件发布订阅、本地存储。
- Vue3：Composition API、组件通信、Pinia、Router、computed/watch、nextTick、动态组件。
- 工程能力：模块拆分、Mock 数据、本地持久化、路由懒加载、错误状态、空状态、加载状态。

## 2. 推荐技术栈

- 构建工具：Vite
- 框架：Vue3
- 语言：JavaScript
- 路由：Vue Router
- 状态管理：Pinia
- 样式：原生 CSS 或 SCSS
- 图标：lucide-vue-next
- 本地存储：localStorage，进阶可换 IndexedDB
- Mock 数据：本地 JSON + Promise 模拟请求
- 可选库：dayjs、marked、DOMPurify、sortablejs

如果你想最大化练手价值，建议先不用 UI 组件库，所有布局和基础组件都自己写。

## 3. 核心页面

### 3.1 今日工作台 `/dashboard`

目标：进入项目后的总览页，展示今天该刷什么、哪些知识点薄弱、最近投递进展。

主要模块：

- 顶部统计：待复习题数、今日算法、进行中投递、最近模拟面试分数。
- 今日计划：按优先级列出 CSS、JS、Vue、网络、算法任务。
- 薄弱知识点：用条形图或雷达图展示各分类掌握度。
- 最近面经：展示最近整理的公司面经和复盘状态。
- 快捷入口：开始模拟面试、继续算法题、添加投递记录。

可练习点：

- Grid 仪表盘布局。
- 统计数据通过 computed 派生。
- 空状态、加载状态、异常状态。
- 简单图表可用 CSS 或 SVG 手写。

### 3.2 面试题库 `/questions`

目标：管理 CSS、JS、Vue、计算机网络四类高频题，支持筛选、搜索、收藏和复习状态。

主要模块：

- 左侧分类：CSS、JavaScript、Vue、Network、Algorithm。
- 顶部筛选：难度、标签、是否收藏、是否已掌握。
- 搜索框：输入关键词后防抖搜索。
- 题目列表：题目、分类、标签、掌握状态、上次复习时间。
- 右侧详情：答案、追问、易错点、自己的补充笔记。

可练习点：

- 防抖搜索。
- 多条件筛选。
- 列表虚拟滚动。
- 父子组件通信。
- 收藏和复习状态持久化。

### 3.3 算法练习 `/algorithms`

目标：整理前端实习常见算法题，并在页面内完成思路、代码、测试用例记录。

主要模块：

- 题目列表：题号、名称、难度、标签、完成状态。
- 题目详情：题意、示例、约束、思路模板。
- 代码编辑区：先用 textarea 实现，进阶再接 Monaco Editor。
- 测试用例：输入、期望输出、运行结果。
- 复盘区：复杂度、错因、二刷日期。

可练习点：

- Tab 切换。
- 本地代码草稿保存。
- Promise 模拟运行状态。
- 题目完成率统计。
- 复杂列表和详情联动。

### 3.4 面经笔记 `/experiences`

目标：把牛客、笔记、真实面试记录整理成可复盘的面经库。

主要模块：

- 公司列表：公司、岗位、轮次、时间、结果。
- 时间线：一面、二面、HR 面、Offer 或挂。
- 面试问题：按 CSS、JS、Vue、网络、项目、算法分类。
- 复盘笔记：答得好的点、卡住的点、下次改进。
- 导入导出：支持 JSON 导入导出。

可练习点：

- 时间线组件。
- 标签编辑。
- JSON 导入导出。
- Markdown 预览。
- 复杂表单校验。

### 3.5 投递看板 `/applications`

目标：管理实习投递流程，用拖拽看板展示每家公司当前进度。

看板列：

- 待投递
- 已投递
- 笔试
- 一面
- 二面
- HR 面
- Offer
- 已结束

卡片字段：

- 公司名称
- 岗位名称
- 城市
- 投递渠道
- 截止时间
- 当前状态
- 下一步动作
- 备注

可练习点：

- HTML5 Drag and Drop 或 pointer 事件拖拽。
- 数组移动、状态同步。
- 乐观更新和撤销。
- 横向滚动布局。
- 数据持久化。

### 3.6 模拟面试 `/mock-interview`

目标：从题库中随机抽题，按真实面试节奏进行限时模拟，并生成复盘记录。

主要模块：

- 模式选择：基础八股、Vue 专项、网络专项、项目深挖、算法快问。
- 抽题面板：当前问题、追问、提示。
- 计时器：当前题用时、总用时。
- 作答笔记：记录自己的回答大纲。
- 评分表：准确性、完整性、表达清晰度、项目结合度。
- 面试报告：本次问题、得分、薄弱点、复习建议。

可练习点：

- 随机抽题算法。
- 倒计时和暂停恢复。
- 表单状态管理。
- 动态生成报告。
- 组件状态重置。

## 4. 数据模型

### 4.1 Question

```js
{
  id: 'q_js_001',
  title: '介绍一下事件循环',
  category: 'JavaScript',
  difficulty: 'medium',
  tags: ['event-loop', 'promise', 'async'],
  answer: '...',
  followUps: ['宏任务和微任务有哪些？', 'Promise.then 属于什么任务？'],
  pitfalls: ['不要把 async 函数本身说成微任务'],
  mastered: false,
  starred: true,
  lastReviewedAt: '2026-05-13'
}
```

### 4.2 AlgorithmProblem

```js
{
  id: 'lc_003',
  title: '无重复字符的最长子串',
  leetcodeUrl: 'https://leetcode.cn/problems/longest-substring-without-repeating-characters/',
  difficulty: 'medium',
  tags: ['sliding-window', 'hash-map'],
  status: 'todo',
  codeDraft: '',
  notes: '',
  testCases: [
    { input: '"abcabcbb"', expected: 3 }
  ]
}
```

### 4.3 Experience

```js
{
  id: 'exp_001',
  company: '字节跳动',
  role: '前端实习生',
  city: '上海',
  date: '2026-04-18',
  round: '一面',
  result: 'pending',
  questions: [
    { category: 'Vue', content: 'Vue3 响应式原理是什么？' }
  ],
  review: {
    good: '项目讲得比较完整',
    stuck: '网络缓存回答不够细',
    action: '补强强缓存和协商缓存'
  }
}
```

### 4.4 Application

```js
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
}
```

### 4.5 MockSession

```js
{
  id: 'mock_001',
  mode: 'Vue 专项',
  startedAt: '2026-05-13 20:00',
  duration: 1800,
  questionIds: ['q_vue_001', 'q_vue_002'],
  scores: {
    accuracy: 4,
    completeness: 3,
    expression: 4,
    projectLink: 3
  },
  summary: '响应式原理掌握较好，但 diff 和 key 的追问不够稳定。'
}
```

## 5. 推荐目录结构

```txt
src/
  assets/
  components/
    common/
      AppButton.vue
      AppDialog.vue
      AppDrawer.vue
      EmptyState.vue
      SearchInput.vue
      TagPill.vue
    dashboard/
      StatCard.vue
      TodayPlan.vue
      WeaknessChart.vue
    questions/
      QuestionList.vue
      QuestionDetail.vue
      QuestionFilters.vue
    algorithms/
      ProblemList.vue
      CodeWorkspace.vue
      TestCasePanel.vue
    experiences/
      ExperienceTimeline.vue
      ExperienceEditor.vue
    applications/
      KanbanBoard.vue
      KanbanColumn.vue
      ApplicationCard.vue
    mock/
      InterviewTimer.vue
      QuestionPrompt.vue
      ScorePanel.vue
  data/
    questions.js
    algorithms.js
    experiences.js
    applications.js
  router/
    index.js
  stores/
    questionStore.js
    algorithmStore.js
    applicationStore.js
    mockStore.js
  utils/
    storage.js
    debounce.js
    virtualList.js
    promisePool.js
    date.js
  views/
    DashboardView.vue
    QuestionsView.vue
    AlgorithmsView.vue
    ExperiencesView.vue
    ApplicationsView.vue
    MockInterviewView.vue
  App.vue
  main.js
```

## 6. 页面布局规范

整体风格：简洁、工作台式、信息密度适中，不做营销首页。

布局：

- 左侧固定导航，宽度 220px。
- 顶部为页面标题、搜索、快捷操作。
- 主内容区使用 12 栅格或 CSS Grid。
- 列表页采用左列表右详情结构。
- 看板页采用横向滚动列。

颜色：

- 背景：`#f6f8fb`
- 主文本：`#172033`
- 次级文本：`#667085`
- 主色：`#2563eb`
- 成功：`#16a34a`
- 警告：`#f59e0b`
- 危险：`#dc2626`
- 卡片边框：`#e5e7eb`

组件圆角建议 8px，不要做过度圆润的胶囊风格。

## 7. 核心功能优先级

### MVP 必做

1. 左侧导航 + 六个页面路由。
2. 题库的搜索、筛选、收藏、掌握状态。
3. 投递看板的卡片新增、编辑、拖拽换列。
4. 面经笔记的新增、编辑、分类展示。
5. 模拟面试的随机抽题、计时、评分、生成报告。
6. 所有数据 localStorage 持久化。

### 进阶功能

1. 题库虚拟列表。
2. JSON 导入导出。
3. Markdown 预览。
4. 算法代码草稿自动保存。
5. 模拟请求加载态和错误重试。
6. 亮色/暗色主题切换。

## 8. 必写工具函数

这些函数建议手写，面试时也能直接讲。

```js
// 防抖搜索
export function debounce(fn, delay = 300) {}

// 节流滚动
export function throttle(fn, delay = 300) {}

// 深拷贝本地数据
export function deepClone(value, cache = new WeakMap()) {}

// Promise 并发控制
export function promisePool(tasks, limit = 3) {}

// localStorage 带版本号封装
export function createStorage(namespace, version) {}

// 虚拟列表区间计算
export function getVisibleRange(scrollTop, itemHeight, containerHeight, buffer = 5) {}

// 数组元素移动，用于看板拖拽
export function moveItem(list, fromIndex, toIndex) {}
```

## 9. 面试可讲亮点

### 亮点 1：题库筛选和虚拟列表

可以这样讲：

题库数据量变大后，如果一次性渲染所有题目，滚动和筛选会卡顿。我把题目列表拆成筛选层和渲染层，搜索使用 debounce，列表区域只渲染可视范围加 buffer 的数据，通过 scrollTop 计算 startIndex 和 endIndex。

### 亮点 2：投递看板拖拽

可以这样讲：

看板拖拽本质是两个状态变化：卡片从原列删除，再插入目标列。我没有直接操作 DOM，而是让拖拽事件只负责计算来源和目标，最终通过更新数据驱动视图刷新，这样更符合 Vue 的响应式模型。

### 亮点 3：本地持久化

可以这样讲：

项目没有后端，所以我封装了 storage 工具，统一处理 namespace、版本号、序列化、异常兜底。后续如果接接口，只需要替换数据层，不需要改页面组件。

### 亮点 4：模拟面试状态机

可以这样讲：

模拟面试不是简单表单，我把它抽象成 idle、running、paused、finished 几种状态，计时器、当前题、评分和报告都围绕状态变化更新，避免多个布尔值互相冲突。

## 10. 七天手写计划

### Day 1：项目初始化和基础布局

- Vite 创建 Vue3 项目。
- 配置 Router、Pinia。
- 完成左侧导航、顶部栏、主内容容器。
- 写基础按钮、标签、弹窗、空状态组件。

### Day 2：题库页面

- 准备 CSS、JS、Vue、网络题目数据。
- 完成搜索、筛选、收藏、掌握状态。
- 完成题目详情面板。
- 写 debounce。

### Day 3：投递看板

- 完成看板列和卡片。
- 实现新增、编辑、删除。
- 实现拖拽换列。
- 写 moveItem。

### Day 4：面经笔记

- 完成公司面经列表。
- 完成时间线和详情抽屉。
- 完成面经编辑表单。
- 支持 JSON 导入导出。

### Day 5：算法练习

- 完成算法题列表和详情。
- 完成代码草稿、测试用例、复盘笔记。
- 实现自动保存。
- 整理 LeetCode 链接。

### Day 6：模拟面试

- 完成模式选择、随机抽题、计时器。
- 完成评分和报告生成。
- 写状态机逻辑。

### Day 7：优化和面试材料

- 加虚拟列表。
- 加主题切换或响应式适配。
- 补充错误状态和 loading。
- 整理 README 和项目亮点。

## 11. 简历描述示例

OfferPilot 前端实习训练工作台  
技术栈：Vue3、JavaScript、Pinia、Vue Router、Vite、CSS Grid、localStorage

- 设计并实现面试题库、算法练习、面经笔记、投递看板和模拟面试模块，覆盖实习求职全流程。
- 封装本地存储层，支持题目收藏、复习状态、投递进度和模拟面试报告持久化。
- 实现题库多条件筛选和防抖搜索，并通过虚拟列表优化大量题目渲染性能。
- 基于数据驱动实现投递看板拖拽流转，支持卡片新增、编辑、换列和撤销。
- 将模拟面试流程抽象为状态机，支持随机抽题、计时、评分和复盘报告生成。

## 12. 页面图清单

本项目建议准备以下页面视觉稿：

1. 今日工作台
2. 面试题库
3. 算法练习
4. 面经笔记
5. 投递看板
6. 模拟面试

页面设计方向：桌面端优先，左侧导航，信息密度适中，适合前端实习生每日高频使用。
