<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <DashboardNav />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold mb-8">Dashboard</h1>
      
      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="card">
          <div class="text-sm text-gray-500">Total Events</div>
          <div class="text-3xl font-bold text-doomly-600">{{ stats.total_events || 0 }}</div>
        </div>
        <div class="card">
          <div class="text-sm text-gray-500">Total Orders</div>
          <div class="text-3xl font-bold text-doomly-600">{{ stats.total_orders || 0 }}</div>
        </div>
        <div class="card">
          <div class="text-sm text-gray-500">Total Revenue</div>
          <div class="text-3xl font-bold text-doomly-600">€{{ (stats.total_revenue || 0).toFixed(2) }}</div>
        </div>
        <div class="card">
          <div class="text-sm text-gray-500">Total Attendees</div>
          <div class="text-3xl font-bold text-doomly-600">{{ stats.total_attendees || 0 }}</div>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="card mb-8">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="flex gap-4">
          <router-link to="/dashboard/events/new" class="btn-primary">
            + Create New Event
          </router-link>
          <router-link to="/dashboard/orders" class="btn-secondary">
            View Orders
          </router-link>
        </div>
      </div>
      
      <!-- Recent Orders -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Recent Orders</h2>
        <div v-if="!stats.recent_orders?.length" class="text-gray-500 text-center py-8">
          No orders yet
        </div>
        <table v-else class="w-full">
          <thead>
            <tr class="text-left text-sm text-gray-500 border-b">
              <th class="pb-2">Order</th>
              <th class="pb-2">Customer</th>
              <th class="pb-2">Amount</th>
              <th class="pb-2">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in stats.recent_orders" :key="order.id" class="border-b">
              <td class="py-3">{{ order.order_number }}</td>
              <td class="py-3">{{ order.first_name }} {{ order.last_name }}</td>
              <td class="py-3">€{{ order.total_amount.toFixed(2) }}</td>
              <td class="py-3">
                <span :class="['px-2 py-1 rounded text-sm', 
                  order.status === 'completed' ? 'bg-green-100 text-green-800' : 
                  order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800']">
                  {{ order.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import DashboardNav from '@/components/DashboardNav.vue'

const stats = ref({})

onMounted(async () => {
  try {
    const { data } = await api.get('/dashboard/overview')
    stats.value = data
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  }
})
</script>
