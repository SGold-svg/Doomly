<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4">
    <div class="max-w-md w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-doomly-600">Create Account</h1>
        <p class="text-gray-600 mt-2">Start managing events today</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="card">
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {{ error }}
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="label">First Name</label>
            <input v-model="form.first_name" type="text" class="input" required>
          </div>
          <div>
            <label class="label">Last Name</label>
            <input v-model="form.last_name" type="text" class="input" required>
          </div>
        </div>
        
        <div class="mb-4">
          <label class="label">Email</label>
          <input v-model="form.email" type="email" class="input" placeholder="you@example.com" required>
        </div>
        
        <div class="mb-4">
          <label class="label">Password</label>
          <input v-model="form.password" type="password" class="input" placeholder="Min 8 characters" required>
        </div>
        
        <div class="mb-6">
          <label class="flex items-center">
            <input v-model="form.create_organization" type="checkbox" class="mr-2">
            <span class="text-sm text-gray-600">Create an organization</span>
          </label>
        </div>
        
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>
      
      <p class="text-center mt-6 text-gray-600">
        Already have an account? 
        <router-link to="/login" class="text-doomly-600 hover:text-doomly-700 font-medium">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  create_organization: true,
})

const error = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  loading.value = true
  
  try {
    await authStore.register(form.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
