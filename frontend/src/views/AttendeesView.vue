<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">Attendees</h1>
      
      <div class="card mb-6">
        <div class="flex justify-between items-center">
          <div class="flex gap-4">
            <input v-model="search" type="text" class="input w-64" placeholder="Search attendees...">
            <select v-model="filterCheckedIn" class="input w-40">
              <option value="">All</option>
              <option value="true">Checked In</option>
              <option value="false">Not Checked In</option>
            </select>
          </div>
          <button @click="exportAttendees" class="btn-secondary">Export CSV</button>
        </div>
      </div>
      
      <div v-if="loading" class="text-center py-12">Loading...</div>
      <div v-else-if="!attendees.length" class="card text-center py-12 text-gray-500">
        No attendees found
      </div>
      <div v-else class="card">
        <table class="w-full">
          <thead>
            <tr class="text-left text-sm text-gray-500 border-b">
              <th class="pb-3">Name</th>
              <th class="pb-3">Email</th>
              <th class="pb-3">Ticket</th>
              <th class="pb-3">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="attendee in attendees" :key="attendee.id" class="border-b">
              <td class="py-3">{{ attendee.first_name }} {{ attendee.last_name }}</td>
              <td class="py-3">{{ attendee.email }}</td>
              <td class="py-3">{{ attendee.ticket_type?.name }}</td>
              <td class="py-3">
                <span :class="['px-2 py-1 rounded text-sm', 
                  attendee.is_checked_in ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600']">
                  {{ attendee.is_checked_in ? 'Checked In' : 'Not Checked In' }}
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
import { useRoute } from 'vue-router'
import api from '@/api'
import DashboardNav from '@/components/DashboardNav.vue'

const route = useRoute()

const attendees = ref([])
const loading = ref(true)
const search = ref('')
const filterCheckedIn = ref('')

const loadAttendees = async () => {
  loading.value = true
  try {
    const params = { search: search.value }
    if (filterCheckedIn.value) {
      params.checked_in = filterCheckedIn.value
    }
    const { data } = await api.get(`/attendees/event/${route.params.eventId}`, { params })
    attendees.value = data.attendees
  } finally {
    loading.value = false
  }
}

const exportAttendees = () => {
  window.open(`/api/attendees/event/${route.params.eventId}/export`, '_blank')
}

onMounted(() => {
  loadAttendees()
})
</script>
