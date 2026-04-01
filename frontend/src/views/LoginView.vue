<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-doomly-600">Welcome Back</h1>
        <p class="text-gray-600 mt-2">Sign in to your Doomly account</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="card">
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {{ error }}
        </div>
        
        <div class="mb-4">
          <label class="label">Email</label>
          <input v-model="form.email" type="email" class="input" placeholder="you@example.com" required>
        </div>
        
        <div class="mb-6">
          <label class="label">Password</label>
          <input v-model="form.password" type="password" class="input" placeholder="••••••••" required>
        </div>
        
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        
        <div class="mt-4 text-center text-sm">
          <router-link to="/forgot-password" class="text-doomly-600 hover:text-doomly-700">
            Forgot password?
          </router-link>
        </div>
      </form>
      
      <p class="text-center mt-6 text-gray-600">
        Don't have an account? 
        <router-link to="/register" class="text-doomly-600 hover:text-doomly-700 font-medium">
          Sign up
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
})

const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  try {
    await authStore.login(form.value.email, form.value.password)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
