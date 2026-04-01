<template>
  <div class="bg-white border-b">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/" class="flex items-center">
            <span class="text-2xl font-bold text-doomly-600">D</span>
            <span class="text-2xl font-bold text-gray-900">oomly</span>
          </router-link>
          <div class="hidden md:flex ml-10 space-x-8">
            <router-link to="/dashboard" class="text-gray-600 hover:text-doomly-600 px-3 py-2">Dashboard</router-link>
            <router-link to="/dashboard/events" class="text-gray-600 hover:text-doomly-600 px-3 py-2">My Events</router-link>
            <router-link to="/dashboard/orders" class="text-gray-600 hover:text-doomly-600 px-3 py-2">Orders</router-link>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-gray-600">Welcome, {{ authStore.user?.first_name }}</span>
          <button @click="logout" class="text-gray-600 hover:text-doomly-600">Logout</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>
