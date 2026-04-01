<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">Check-in</h1>
      
      <div class="card mb-6">
        <h2 class="text-lg font-semibold mb-4">Scan Ticket</h2>
        <div class="flex gap-4">
          <input v-model="ticketNumber" type="text" class="input flex-1" placeholder="Enter ticket number..." @keyup.enter="checkIn">
          <button @click="checkIn" class="btn-primary">Check In</button>
        </div>
        <div v-if="result" :class="['mt-4 p-4 rounded', result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
          {{ result.message }}
        </div>
      </div>
      
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="card text-center">
          <div class="text-sm text-gray-500">Total</div>
          <div class="text-3xl font-bold">{{ stats.total_attendees }}</div>
        </div>
        <div class="card text-center">
          <div class="text-sm text-gray-500">Checked In</div>
          <div class="text-3xl font-bold text-green-600">{{ stats.checked_in }}</div>
        </div>
        <div class="card text-center">
          <div class="text-sm text-gray-500">Check-in Rate</div>
          <div class="text-3xl font-bold text-doomly-600">{{ stats.rate }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import DashboardNav from '@/components/DashboardNav.vue'

const route = useRoute()

const ticketNumber = ref('')
const result = ref(null)
const stats = ref({ total_attendees: 0, checked_in: 0, rate: 0 })

const checkIn = async () => {
  if (!ticketNumber.value) return
  
  try {
    const { data } = await api.post(`/attendees/ticket/${ticketNumber.value}/check-in`)
    result.value = { success: true, message: `${data.attendee.first_name} ${data.attendee.last_name} checked in!` }
    ticketNumber.value = ''
    loadStats()
  } catch (error) {
    result.value = { success: false, message: error.response?.data?.error || 'Check-in failed' }
  }
}

const loadStats = async () => {
  try {
    const { data } = await api.get(`/checkin/event/${route.params.eventId}/stats`)
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>
