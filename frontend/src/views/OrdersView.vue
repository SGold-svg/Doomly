<template>
  <div class="min-h-screen bg-gray-50">
    <DashboardNav />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">My Orders</h1>
      </div>
      
      <div v-if="loading" class="text-center py-12">Loading orders...</div>
      <div v-else-if="!orders.length" class="card text-center py-12">
        <p class="text-gray-500">You haven't placed any orders yet.</p>
        <router-link to="/events" class="btn-primary mt-4 inline-block">Browse Events</router-link>
      </div>
      <div v-else class="card">
        <table class="w-full">
          <thead>
            <tr class="text-left text-sm text-gray-500 border-b">
              <th class="pb-3">Order</th>
              <th class="pb-3">Event</th>
              <th class="pb-3">Tickets</th>
              <th class="pb-3">Amount</th>
              <th class="pb-3">Status</th>
              <th class="pb-3">Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id" class="border-b">
              <td class="py-4">{{ order.order_number }}</td>
              <td class="py-4">{{ order.event?.title || 'Event' }}</td>
              <td class="py-4">{{ order.quantity }}</td>
              <td class="py-4">€{{ order.total_amount.toFixed(2) }}</td>
              <td class="py-4">
                <span :class="['px-2 py-1 rounded text-sm', 
                  order.status === 'completed' ? 'bg-green-100 text-green-800' : 
                  order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800']">
                  {{ order.status }}
                </span>
              </td>
              <td class="py-4">{{ formatDate(order.created_at) }}</td>
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
import { format } from 'date-fns'
import DashboardNav from '@/components/DashboardNav.vue'

const orders = ref([])
const loading = ref(true)

const formatDate = (dateStr) => format(new Date(dateStr), 'MMM d, yyyy')

onMounted(async () => {
  try {
    const { data } = await api.get('/orders/my-orders')
    orders.value = data.orders
  } finally {
    loading.value = false
  }
})
</script>
