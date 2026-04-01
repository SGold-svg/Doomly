<template>
  <div class="min-h-screen bg-gray-50">
    <DashboardNav />
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">My Events</h1>
        <router-link to="/dashboard/events/new" class="btn-primary">+ Create Event</router-link>
      </div>
      
      <div v-if="loading" class="text-center py-12">Loading events...</div>
      <div v-else-if="!events.length" class="card text-center py-12">
        <p class="text-gray-500 mb-4">You haven't created any events yet.</p>
        <router-link to="/dashboard/events/new" class="btn-primary">Create Your First Event</router-link>
      </div>
      <div v-else class="grid gap-4">
        <div v-for="event in events" :key="event.id" class="card flex justify-between items-center">
          <div>
            <h3 class="text-lg font-semibold">{{ event.title }}</h3>
            <p class="text-sm text-gray-500">
              {{ formatDate(event.start_date) }}
              <span v-if="event.city"> • {{ event.city }}</span>
            </p>
            <div class="flex gap-2 mt-2">
              <span :class="['px-2 py-1 rounded text-xs', 
                event.is_published ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600']">
                {{ event.is_published ? 'Published' : 'Draft' }}
              </span>
              <span v-if="event.is_sold_out" class="px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                Sold Out
              </span>
            </div>
          </div>
          <div class="flex gap-2">
            <router-link :to="`/dashboard/event/${event.id}/edit`" class="btn-secondary">Edit</router-link>
            <router-link :to="`/dashboard/attendees/${event.id}`" class="btn-secondary">Attendees</router-link>
            <router-link :to="`/dashboard/checkin/${event.id}`" class="btn-secondary">Check-in</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEventsStore } from '@/stores/events'
import { format } from 'date-fns'
import DashboardNav from '@/components/DashboardNav.vue'

const eventsStore = useEventsStore()
const events = ref([])
const loading = ref(true)

const formatDate = (dateStr) => format(new Date(dateStr), 'MMM d, yyyy')

onMounted(async () => {
  try {
    await eventsStore.fetchMyEvents()
    events.value = eventsStore.myEvents
  } finally {
    loading.value = false
  }
})
</script>
