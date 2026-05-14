import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'offerpilot_token'
const SESSION_KEY = 'offerpilot_session'

function getToken() {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) return token

  try {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY))
    return session?.accessToken || session?.token || ''
  } catch {
    return ''
  }
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(SESSION_KEY)
}

function getErrorMessage(error) {
  if (error.response?.data?.message) return error.response.data.message
  if (error.message?.includes('timeout')) return '请求超时，请稍后重试'
  if (error.message?.includes('Network Error')) return '网络异常，请检查接口地址'
  return error.message || '请求失败'
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function isApifoxMockResponse(response) {
  const mockUrl = import.meta.env.VITE_APIFOX_MOCK_BASE_URL || ''
  return Boolean(import.meta.env.DEV && mockUrl.includes('4523') && response.data?.data)
}

request.interceptors.request.use(
  (config) => {
    const token = getToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const body = response.data

    if (body && typeof body.code !== 'undefined') {
      if (body.code === 0) return body.data

      if (isApifoxMockResponse(response)) {
        console.info(`[OfferPilot] Apifox mock returned code ${body.code}; using response.data for local integration.`)
        return body.data
      }

      ElMessage.error(body.message || '请求失败')
      return Promise.reject(body)
    }

    return body
  },
  (error) => {
    const status = error.response?.status
    const message = getErrorMessage(error)

    if (status === 401) {
      clearAuth()
      ElMessage.error('登录状态已失效，请重新登录')

      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export default request
