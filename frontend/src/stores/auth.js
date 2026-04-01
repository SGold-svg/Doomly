import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    loading: false,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isOrganizer: (state) => state.user?.organization !== null,
  },
  
  actions: {
    async login(email, password) {
      this.loading = true
      try {
        const { data } = await api.post('/auth/login', { email, password })
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return data
      } finally {
        this.loading = false
      }
    },
    
    async register(userData) {
      this.loading = true
      try {
        const { data } = await api.post('/auth/register', userData)
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return data
      } finally {
        this.loading = false
      }
    },
    
    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
      } catch (error) {
        this.logout()
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
