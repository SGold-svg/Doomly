<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <router-link to="/dashboard/events" class="text-doomly-600 hover:text-doomly-700 mb-4 inline-block">
        ← Back to Events
      </router-link>
      
      <h1 class="text-3xl font-bold mb-8">Event Details</h1>
      
      <div v-if="loading" class="text-center py-12">Loading event...</div>
      <div v-else-if="event" class="card">
        <h2 class="text-2xl font-bold mb-4">{{ event.title }}</h2>
        <p class="text-gray-600 mb-6">{{ event.description }}</p>
        
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div>
            <span class="text-sm text-gray-500">Date</span>
            <p>{{ formatDate(event.start_date) }}</p>
          </div>
          <div>
            <span class="text-sm text-gray-500">Location</span>
            <p>{{ event.location?.venue_name || (event.is_online ? 'Online' : 'TBD') }}</p>
          </div>
        </div>
        
        <div class="mb-6">
          <h3 class="font-semibold mb-2">Tickets</h3>
          <div class="space-y-2">
            <div v-for="ticket in event.tickets" :key="ticket.id" class="flex justify-between items-center p-3 bg-gray-50 rounded">
              <div>
                <span class="font-medium">{{ ticket.name }}</span>
                <span v-if="ticket.description" class="text-sm text-gray-500 ml-2">{{ ticket.description }}</span>
              </div>
              <div>
                <span class="font-bold">{{ ticket.is_free ? 'Free' : `€${ticket.price}` }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <router-link :to="`/checkout/${event.slug}`" class="btn-primary inline-block">
          Get Tickets
        </router-link>
      </div>
      <div v-else class="card text-center py-12 text-gray-500">
        Event not found
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEventsStore } from '@/stores/events'
import { format } from 'date-fns'

const route = useRoute()
const eventsStore = useEventsStore()

const event = ref(null)
const loading = ref(true)

const formatDate = (dateStr) => format(new Date(dateStr), 'EEEE, MMMM d, yyyy \'at\' h:mm a')

onMounted(async () => {
  try {
    event.value = await eventsStore.fetchEvent(route.params.slug)
  } finally {
    loading.value = false
  }
})
</script>
