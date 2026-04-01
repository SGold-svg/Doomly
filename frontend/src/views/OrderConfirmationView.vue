<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12">
    <div class="max-w-md w-full text-center">
      <div class="text-6xl mb-6">🎉</div>
      <h1 class="text-3xl font-bold text-green-600 mb-4">Order Confirmed!</h1>
      <p class="text-gray-600 mb-6">Thank you for your order. Your tickets have been sent to your email.</p>
      
      <div v-if="order" class="card text-left mb-6">
        <h2 class="text-lg font-semibold mb-4">Order #{{ order.order_number }}</h2>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">Status</span>
            <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">{{ order.status }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Tickets</span>
            <span>{{ order.quantity }}</span>
          </div>
          <div class="flex justify-between font-bold">
            <span>Total</span>
            <span>€{{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      
      <router-link to="/events" class="btn-primary inline-block">
        Browse More Events
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const order = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get(`/orders/${route.params.orderNumber}`)
    order.value = data.order
  } catch (error) {
    console.error('Failed to load order:', error)
  }
})
</script>
