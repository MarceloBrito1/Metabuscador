import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '../api'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  async function login(username, password) {
    const resp = await authAPI.login(username, password)
    token.value = resp.data.access_token
    localStorage.setItem('token', token.value)
    const meResp = await authAPI.me()
    user.value = meResp.data
    router.push('/search')
  }

  async function register(username, email, password) {
    await authAPI.register({ username, email, password })
    await login(username, password)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  async function fetchUser() {
    if (token.value && !user.value) {
      try {
        const resp = await authAPI.me()
        user.value = resp.data
      } catch {
        logout()
      }
    }
  }

  return { user, token, login, register, logout, fetchUser }
})
