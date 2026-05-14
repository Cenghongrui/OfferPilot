import { createServer } from 'node:http'
import { randomUUID } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const DATA_FILE = join(__dirname, 'data.json')
const HOST = process.env.HOST || '127.0.0.1'
const PORT = Number(process.env.PORT || 3000)

const initialDb = {
  users: [],
  sessions: {},
  dataByUserId: {}
}

const mockModes = [
  { name: '基础八股', desc: 'CSS / JS / 浏览器基础' },
  { name: 'Vue 专项', desc: '响应式、组件通信、Router' },
  { name: '网络专项', desc: '缓存、跨域、HTTP' },
  { name: '项目深挖', desc: '架构、性能、难点复盘' },
  { name: '算法快问', desc: '数组、栈、滑动窗口' }
]

const questionPool = [
  {
    id: 'mock_q_vue',
    mode: 'Vue 专项',
    title: 'Vue3 响应式原理是什么？',
    prompt: '请从 Proxy、依赖收集、触发更新和视图渲染四个层次讲清楚。',
    followUps: ['ref 和 reactive 的区别？', 'computed 为什么有缓存？'],
    hint: '提示：可以按 get 收集、set 触发、effect 重新执行来组织。'
  },
  {
    id: 'mock_q_network',
    mode: '网络专项',
    title: '浏览器缓存策略如何设计？',
    prompt: '请说明强缓存、协商缓存，以及前端静态资源部署时如何避免缓存问题。',
    followUps: ['no-cache 和 no-store 区别？', 'hash 文件名解决了什么？'],
    hint: '提示：回答里最好带上 Cache-Control、ETag 和构建产物 hash。'
  }
]

function emptyUserData() {
  return {
    questions: [],
    algorithms: [],
    experiences: [],
    applications: [],
    todayPlans: [],
    mockSessions: [],
    notifications: []
  }
}

async function loadDb() {
  try {
    const content = await readFile(DATA_FILE, 'utf8')
    return { ...initialDb, ...JSON.parse(content) }
  } catch {
    return structuredClone(initialDb)
  }
}

async function saveDb(db) {
  await mkdir(__dirname, { recursive: true })
  await writeFile(DATA_FILE, JSON.stringify(db, null, 2))
}

function sendJson(res, status, body) {
  res.writeHead(status, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,DELETE,OPTIONS',
    'Content-Type': 'application/json; charset=utf-8'
  })
  res.end(JSON.stringify(body))
}

function ok(res, data = null) {
  sendJson(res, 200, { code: 0, message: 'ok', data })
}

function fail(res, status, code, message) {
  sendJson(res, status, { code, message, data: null })
}

async function readBody(req) {
  const chunks = []
  for await (const chunk of req) chunks.push(chunk)
  if (!chunks.length) return {}

  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'))
  } catch {
    return {}
  }
}

function publicUser(user) {
  const { password, ...safeUser } = user
  return safeUser
}

function getToken(req) {
  const authorization = req.headers.authorization || ''
  return authorization.startsWith('Bearer ') ? authorization.slice(7) : ''
}

function getCurrentUser(db, req) {
  const token = getToken(req)
  const userId = db.sessions[token]
  if (!userId) return null
  return db.users.find((user) => user.id === userId) || null
}

function getUserData(db, userId) {
  if (!db.dataByUserId[userId]) db.dataByUserId[userId] = emptyUserData()
  return db.dataByUserId[userId]
}

function paginate(list, query) {
  const page = Number(query.get('page') || 1)
  const pageSize = Number(query.get('pageSize') || list.length || 20)
  return {
    list: list.slice((page - 1) * pageSize, page * pageSize),
    pagination: { page, pageSize, total: list.length }
  }
}

function today() {
  return new Date().toISOString().slice(0, 10)
}

function dashboardOverview(data) {
  const reviewTodoCount = data.questions.filter((item) => !item.mastered).length
  const algorithmSolvedCount = data.algorithms.filter((item) => item.status === 'done').length
  const applicationCount = data.applications.length
  const mockInterviewCount = data.mockSessions.length
  const weakPoints = data.questions
    .filter((item) => !item.mastered)
    .slice(0, 5)
    .map((item) => ({ name: item.title, mastery: 30 }))

  return {
    stats: {
      studyHoursToday: 0,
      reviewTodoCount,
      algorithmSolvedCount,
      applicationCount,
      mockInterviewCount
    },
    changes: {
      studyHoursToday: 0,
      reviewTodoCount: 0,
      algorithmSolvedCount: 0,
      applicationCount: 0,
      mockInterviewCount: 0
    },
    mastery: {
      overall: data.questions.length ? Math.round(((data.questions.length - reviewTodoCount) / data.questions.length) * 100) : 0
    },
    weakPoints
  }
}

function applicationStats(applications) {
  return {
    total: applications.length,
    interviewing: applications.filter((item) => ['interview_1', 'interview_2', 'hr'].includes(item.stage)).length,
    offer: applications.filter((item) => item.stage === 'offer').length
  }
}

function questionStats(questions) {
  return {
    total: questions.length,
    starred: questions.filter((item) => item.starred).length,
    reviewTodo: questions.filter((item) => !item.mastered).length
  }
}

function algorithmStats(algorithms) {
  const done = algorithms.filter((item) => item.status === 'done').length
  return {
    total: algorithms.length,
    completionRate: algorithms.length ? Math.round((done / algorithms.length) * 100) : 0,
    reviewCountThisWeek: algorithms.filter((item) => item.notes).length
  }
}

function profileOverview(user, data) {
  const reports = data.mockSessions.filter((item) => item.report)
  const averageScore = reports.length
    ? Math.round(reports.reduce((sum, item) => sum + Number(item.report.total || 0), 0) / reports.length)
    : 0

  return {
    user: publicUser(user),
    overview: {
      reviewTodoCount: data.questions.filter((item) => !item.mastered).length,
      activeApplicationCount: data.applications.filter((item) => item.stage !== 'closed' && item.stage !== 'offer').length,
      mockInterviewAverageScore: averageScore
    },
    activities: []
  }
}

function createItem(prefix, payload) {
  return {
    ...payload,
    id: `${prefix}_${randomUUID().slice(0, 8)}`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
}

function updateById(list, id, payload) {
  const item = list.find((entry) => entry.id === id)
  if (!item) return null
  Object.assign(item, payload, { updatedAt: new Date().toISOString() })
  return item
}

function removeById(list, id) {
  const index = list.findIndex((entry) => entry.id === id)
  if (index === -1) return false
  list.splice(index, 1)
  return true
}

async function handleRequest(req, res) {
  if (req.method === 'OPTIONS') {
    sendJson(res, 204, null)
    return
  }

  const db = await loadDb()
  const url = new URL(req.url, `http://${req.headers.host}`)
  const path = url.pathname.replace(/^\/api/, '')
  const body = await readBody(req)

  if (req.method === 'POST' && path === '/auth/register') {
    if (!body.name || !body.email || !body.password) {
      fail(res, 400, 40000, '请填写昵称、邮箱和密码')
      return
    }

    if (db.users.some((user) => user.email === body.email)) {
      fail(res, 409, 40002, '邮箱已注册')
      return
    }

    const user = {
      id: `user_${randomUUID().slice(0, 8)}`,
      name: body.name,
      email: body.email,
      password: body.password,
      goal: '',
      notifications: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    const token = `local_${randomUUID()}`
    db.users.push(user)
    db.sessions[token] = user.id
    db.dataByUserId[user.id] = emptyUserData()
    await saveDb(db)
    ok(res, { user: publicUser(user), accessToken: token })
    return
  }

  if (req.method === 'POST' && path === '/auth/login') {
    const user = db.users.find((entry) => entry.email === body.email && entry.password === body.password)
    if (!user) {
      fail(res, 401, 40001, '邮箱或密码不正确')
      return
    }

    const token = `local_${randomUUID()}`
    db.sessions[token] = user.id
    getUserData(db, user.id)
    await saveDb(db)
    ok(res, { user: publicUser(user), accessToken: token })
    return
  }

  const user = getCurrentUser(db, req)
  if (!user) {
    fail(res, 401, 40100, '未登录或 token 无效')
    return
  }

  const data = getUserData(db, user.id)

  if (req.method === 'POST' && path === '/auth/logout') {
    const token = getToken(req)
    delete db.sessions[token]
    await saveDb(db)
    ok(res, null)
    return
  }

  if (req.method === 'GET' && path === '/users/me') {
    ok(res, publicUser(user))
    return
  }

  if (req.method === 'PATCH' && path === '/users/me') {
    Object.assign(user, {
      name: body.name ?? user.name,
      goal: body.goal ?? user.goal,
      notifications: body.notifications ?? user.notifications,
      updatedAt: new Date().toISOString()
    })
    await saveDb(db)
    ok(res, publicUser(user))
    return
  }

  if (req.method === 'GET' && path === '/dashboard/overview') return ok(res, dashboardOverview(data))
  if (req.method === 'GET' && path === '/dashboard/today-plan') return ok(res, data.todayPlans)

  const planMatch = path.match(/^\/dashboard\/today-plan\/([^/]+)$/)
  if (req.method === 'PATCH' && planMatch) {
    const plan = updateById(data.todayPlans, planMatch[1], { completed: Boolean(body.completed) })
    await saveDb(db)
    ok(res, plan)
    return
  }

  if (path === '/questions/stats' && req.method === 'GET') return ok(res, questionStats(data.questions))
  if (path === '/questions' && req.method === 'GET') return ok(res, paginate(data.questions, url.searchParams))
  if (path === '/questions' && req.method === 'POST') {
    const item = createItem('q', body)
    data.questions.unshift(item)
    await saveDb(db)
    return ok(res, item)
  }

  const questionMatch = path.match(/^\/questions\/([^/]+)(?:\/(star|mastery))?$/)
  if (questionMatch) {
    const [, id, action] = questionMatch
    if (req.method === 'GET') return ok(res, data.questions.find((item) => item.id === id) || null)
    if (req.method === 'DELETE') {
      removeById(data.questions, id)
      await saveDb(db)
      return ok(res, null)
    }
    if (req.method === 'PATCH') {
      const payload = action === 'star' ? { starred: body.starred } : action === 'mastery' ? body : body
      const item = updateById(data.questions, id, payload)
      await saveDb(db)
      return ok(res, item)
    }
  }

  if (path === '/algorithms/stats' && req.method === 'GET') return ok(res, algorithmStats(data.algorithms))
  if (path === '/algorithms' && req.method === 'GET') return ok(res, paginate(data.algorithms, url.searchParams))
  if (path === '/algorithms' && req.method === 'POST') {
    const item = createItem('algo', body)
    data.algorithms.unshift(item)
    await saveDb(db)
    return ok(res, item)
  }

  const algorithmMatch = path.match(/^\/algorithms\/([^/]+)(?:\/(code-draft|run))?$/)
  if (algorithmMatch) {
    const [, id, action] = algorithmMatch
    if (req.method === 'GET') return ok(res, data.algorithms.find((item) => item.id === id) || null)
    if (req.method === 'PATCH') {
      const item = updateById(data.algorithms, id, action === 'code-draft' ? { codeDraft: body.codeDraft } : body)
      await saveDb(db)
      return ok(res, item)
    }
    if (req.method === 'POST' && action === 'run') return ok(res, { status: 'passed', cases: body.testCases || [] })
  }

  if (path === '/experiences/export' && req.method === 'GET') {
    return ok(res, { filename: `offerpilot-experiences-${today()}.json`, list: data.experiences })
  }
  if (path === '/experiences/import' && req.method === 'POST') {
    data.experiences = Array.isArray(body) ? body : body.list || []
    await saveDb(db)
    return ok(res, { imported: data.experiences.length })
  }
  if (path === '/experiences' && req.method === 'GET') return ok(res, paginate(data.experiences, url.searchParams))
  if (path === '/experiences' && req.method === 'POST') {
    const item = createItem('exp', body)
    data.experiences.unshift(item)
    await saveDb(db)
    return ok(res, item)
  }

  const experienceMatch = path.match(/^\/experiences\/([^/]+)$/)
  if (experienceMatch) {
    const id = experienceMatch[1]
    if (req.method === 'GET') return ok(res, data.experiences.find((item) => item.id === id) || null)
    if (req.method === 'PATCH') {
      const item = updateById(data.experiences, id, body)
      await saveDb(db)
      return ok(res, item)
    }
    if (req.method === 'DELETE') {
      removeById(data.experiences, id)
      await saveDb(db)
      return ok(res, null)
    }
  }

  if (path === '/applications/stats' && req.method === 'GET') return ok(res, applicationStats(data.applications))
  if (path === '/applications' && req.method === 'GET') return ok(res, paginate(data.applications, url.searchParams))
  if (path === '/applications' && req.method === 'POST') {
    const item = createItem('app', body)
    data.applications.unshift(item)
    await saveDb(db)
    return ok(res, item)
  }

  const applicationMatch = path.match(/^\/applications\/([^/]+)(?:\/move)?$/)
  if (applicationMatch) {
    const id = applicationMatch[1]
    if (req.method === 'GET') return ok(res, data.applications.find((item) => item.id === id) || null)
    if (req.method === 'PATCH') {
      const item = updateById(data.applications, id, path.endsWith('/move') ? { stage: body.toStage, sortOrder: body.sortOrder } : body)
      await saveDb(db)
      return ok(res, item)
    }
    if (req.method === 'DELETE') {
      removeById(data.applications, id)
      await saveDb(db)
      return ok(res, null)
    }
  }

  if (path === '/mock-interview/modes' && req.method === 'GET') return ok(res, mockModes)
  if (path === '/mock-interview/questions/random' && req.method === 'GET') {
    const mode = url.searchParams.get('mode')
    const scoped = questionPool.filter((item) => !mode || item.mode === mode)
    return ok(res, (scoped.length ? scoped : questionPool)[0])
  }
  if (path === '/mock-interview/stats' && req.method === 'GET') {
    const reports = data.mockSessions.filter((item) => item.report)
    return ok(res, {
      modeCount: mockModes.length,
      totalDuration: data.mockSessions.reduce((sum, item) => sum + Number(item.duration || 0), 0),
      averageScore: reports.length ? Math.round(reports.reduce((sum, item) => sum + Number(item.report.total || 0), 0) / reports.length) : 0
    })
  }
  if (path === '/mock-interview/sessions' && req.method === 'GET') return ok(res, paginate(data.mockSessions, url.searchParams))
  if (path === '/mock-interview/sessions' && req.method === 'POST') {
    const item = createItem('session', { ...body, status: 'running', duration: 0 })
    data.mockSessions.unshift(item)
    await saveDb(db)
    return ok(res, item)
  }

  const sessionMatch = path.match(/^\/mock-interview\/sessions\/([^/]+)(?:\/report)?$/)
  if (sessionMatch) {
    const id = sessionMatch[1]
    if (req.method === 'PATCH') {
      const item = updateById(data.mockSessions, id, body)
      await saveDb(db)
      return ok(res, item)
    }
    if (req.method === 'POST' && path.endsWith('/report')) {
      const session = data.mockSessions.find((item) => item.id === id)
      const total = Object.values(body.scores || {}).reduce((sum, item) => sum + Number(item || 0), 0)
      const report = {
        total,
        question: body.questionId || '本次模拟面试',
        weakness: total < 16 ? '回答结构还可以更完整，追问需要提前准备例子。' : '整体稳定，继续补充项目结合案例。',
        suggestion: '把本次作答笔记沉淀进面经，并复盘薄弱知识点。'
      }
      if (session) Object.assign(session, { report, duration: body.duration, status: 'finished' })
      await saveDb(db)
      return ok(res, report)
    }
  }

  if (path === '/profile/overview' && req.method === 'GET') return ok(res, profileOverview(user, data))
  if (path === '/notifications/unread-count' && req.method === 'GET') return ok(res, { count: data.notifications.filter((item) => !item.read).length })
  if (path === '/notifications' && req.method === 'GET') return ok(res, paginate(data.notifications, url.searchParams))

  const notificationMatch = path.match(/^\/notifications\/([^/]+)\/read$/)
  if (notificationMatch && req.method === 'PATCH') {
    const item = updateById(data.notifications, notificationMatch[1], { read: true })
    await saveDb(db)
    return ok(res, item)
  }

  fail(res, 404, 40400, `接口不存在：${req.method} ${path}`)
}

const server = createServer((req, res) => {
  handleRequest(req, res).catch((error) => {
    console.error(error)
    fail(res, 500, 50000, '本地服务异常')
  })
})

server.listen(PORT, HOST, () => {
  console.log(`OfferPilot local API server running at http://${HOST}:${PORT}`)
})
