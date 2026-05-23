import request from '@/utils/request'

function getTokenForChat() {
  const token = localStorage.getItem('offerpilot_token')
  if (token) return token
  try {
    const session = JSON.parse(localStorage.getItem('offerpilot_session'))
    return session?.accessToken || session?.token || ''
  } catch {
    return ''
  }
}

export const authApi = {
  register(data) {
    return request.post('/auth/register', data)
  },
  login(data) {
    return request.post('/auth/login', data)
  },
  logout() {
    return request.post('/auth/logout')
  },
  getCurrentUser() {
    return request.get('/users/me')
  },
  updateCurrentUser(data) {
    return request.patch('/users/me', data)
  }
}

export const dashboardApi = {
  getOverview() {
    return request.get('/dashboard/overview')
  },
  getTodayPlan() {
    return request.get('/dashboard/today-plan')
  },
  updateTodayPlan(planId, data) {
    return request.patch(`/dashboard/today-plan/${planId}`, data)
  }
}

export const questionApi = {
  getList(params) {
    return request.get('/questions', { params })
  },
  getStats() {
    return request.get('/questions/stats')
  },
  getDetail(questionId) {
    return request.get(`/questions/${questionId}`)
  },
  create(data) {
    return request.post('/questions', data)
  },
  update(questionId, data) {
    return request.patch(`/questions/${questionId}`, data)
  },
  remove(questionId) {
    return request.delete(`/questions/${questionId}`)
  },
  updateStar(questionId, data) {
    return request.patch(`/questions/${questionId}/star`, data)
  },
  updateMastery(questionId, data) {
    return request.patch(`/questions/${questionId}/mastery`, data)
  }
}

export const algorithmApi = {
  getList(params) {
    return request.get('/algorithms', { params })
  },
  getStats() {
    return request.get('/algorithms/stats')
  },
  getDetail(problemId) {
    return request.get(`/algorithms/${problemId}`)
  },
  create(data) {
    return request.post('/algorithms', data)
  },
  update(problemId, data) {
    return request.patch(`/algorithms/${problemId}`, data)
  },
  saveCodeDraft(problemId, data) {
    return request.patch(`/algorithms/${problemId}/code-draft`, data)
  },
  runCases(problemId, data) {
    return request.post(`/algorithms/${problemId}/run`, data)
  }
}

export const experienceApi = {
  getList(params) {
    return request.get('/experiences', { params })
  },
  getDetail(experienceId) {
    return request.get(`/experiences/${experienceId}`)
  },
  create(data) {
    return request.post('/experiences', data)
  },
  update(experienceId, data) {
    return request.patch(`/experiences/${experienceId}`, data)
  },
  remove(experienceId) {
    return request.delete(`/experiences/${experienceId}`)
  },
  exportJson() {
    return request.get('/experiences/export')
  },
  importJson(data) {
    return request.post('/experiences/import', data)
  }
}

export const applicationApi = {
  getList(params) {
    return request.get('/applications', { params })
  },
  getStats() {
    return request.get('/applications/stats')
  },
  getDetail(applicationId) {
    return request.get(`/applications/${applicationId}`)
  },
  create(data) {
    return request.post('/applications', data)
  },
  update(applicationId, data) {
    return request.patch(`/applications/${applicationId}`, data)
  },
  remove(applicationId) {
    return request.delete(`/applications/${applicationId}`)
  },
  move(applicationId, data) {
    return request.patch(`/applications/${applicationId}/move`, data)
  }
}

export const mockInterviewApi = {
  getModes() {
    return request.get('/mock-interview/modes')
  },
  getSessions(params) {
    return request.get('/mock-interview/sessions', { params })
  },
  getSession(sessionId) {
    return request.get(`/mock-interview/sessions/${sessionId}`)
  },
  createSession(data) {
    return request.post('/mock-interview/sessions', data)
  },
  updateSession(sessionId, data) {
    return request.patch(`/mock-interview/sessions/${sessionId}`, data)
  },
  nextQuestion(sessionId) {
    return request.post(`/mock-interview/sessions/${sessionId}/next-question`)
  },
  endSession(sessionId) {
    return request.post(`/mock-interview/sessions/${sessionId}/end`)
  },
  chat(sessionId, message) {
    const token = getTokenForChat()
    const base = import.meta.env.VITE_API_BASE_URL || '/api'
    return fetch(`${base}/mock-interview/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({ message }),
    })
  },
  getStats() {
    return request.get('/mock-interview/stats')
  }
}

export const profileApi = {
  getOverview() {
    return request.get('/profile/overview')
  }
}

export const notificationApi = {
  getList(params) {
    return request.get('/notifications', { params })
  },
  getUnreadCount() {
    return request.get('/notifications/unread-count')
  },
  markAsRead(notificationId) {
    return request.patch(`/notifications/${notificationId}/read`)
  }
}

export default {
  auth: authApi,
  dashboard: dashboardApi,
  question: questionApi,
  algorithm: algorithmApi,
  experience: experienceApi,
  application: applicationApi,
  mockInterview: mockInterviewApi,
  profile: profileApi,
  notification: notificationApi
}
