import { defineStore } from 'pinia'
import { authApi } from '@/api/front'
import { removeToken, setToken } from '@/utils/request'

const USERS_KEY = 'offerpilot_users'
const SESSION_KEY = 'offerpilot_session'

function readJson(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback
  } catch {
    return fallback
  }
}

function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value))
}

function isSameAccount(currentUser, nextUser) {
  if (!currentUser || !nextUser) return false

  const hasComparableId = Boolean(currentUser.id && nextUser.id)
  const hasComparableEmail = Boolean(currentUser.email && nextUser.email)

  if (hasComparableId && currentUser.id !== nextUser.id) return false
  if (hasComparableEmail && currentUser.email !== nextUser.email) return false

  return hasComparableId || hasComparableEmail
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: readJson(SESSION_KEY, null)?.user || readJson(SESSION_KEY, null),
    users: readJson(USERS_KEY, [])
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.user)
  },
  actions: {
    async register(payload) {
      const result = await authApi.register({
        name: payload.name,
        email: payload.email,
        password: payload.password
      })

      const user = result.user || result
      const token = result.accessToken || result.token

      if (token) setToken(token)
      this.user = user
      writeJson(SESSION_KEY, { user, accessToken: token })
    },
    async login({ email, password }) {
      const result = await authApi.login({ email, password })
      const user = result.user || result
      const token = result.accessToken || result.token

      if (token) setToken(token)
      this.user = user
      writeJson(SESSION_KEY, { user, accessToken: token })
    },
    async updateProfile(payload) {
      if (!this.user) return

      const user = await authApi.updateCurrentUser(payload)
      const safeUser = isSameAccount(this.user, user) ? user : payload
      this.user = { ...this.user, ...safeUser }
      this.users = this.users.map((item) => {
        if (item.id !== this.user.id) return item
        return { ...item, ...this.user }
      })
      writeJson(SESSION_KEY, { user: this.user, accessToken: localStorage.getItem('offerpilot_token') })
      writeJson(USERS_KEY, this.users)
    },
    syncCurrentUser(user) {
      if (!isSameAccount(this.user, user)) return

      this.user = { ...this.user, ...user }
      writeJson(SESSION_KEY, { user: this.user, accessToken: localStorage.getItem('offerpilot_token') })
    },
    async logout() {
      try {
        await authApi.logout()
      } catch {
        // The local session should still be cleared even when logout API fails.
      }

      this.user = null
      removeToken()
      localStorage.removeItem(SESSION_KEY)
    }
  }
})
