<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">Browse Events</h1>
        <div class="flex gap-4">
          <input v-model="search" type="text" class="input w-64" placeholder="Search events..." @input="debouncedSearch">
        </div>
      </div>
      
      <div v-if="loading" class="text-center py-12">Loading events...</div>
      <div v-else-if="events.length === 0" class="text-center py-12 text-gray-500">
        No events found. Try adjusting your search.
      </div>
      <div v-else class="grid md:grid-cols-3 gap-6">
        <EventCard v-for="event in events" :key="event.id" :event="event" />
      </div>
      
      <div v-if="pagination.pages > 1" class="flex justify-center gap-2 mt-8">
        <button 
          v-for="page in pagination.pages" 
          :key="page"
          @click="changePage(page)"
          :class="['px-4 py-2 rounded', page === pagination.page ? 'bg-doomly-600 text-white' : 'bg-white']"
        >
          {{ page }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEventsStore } from '@/stores/events'
import EventCard from '@/components/EventCard.vue'

const eventsStore = useEventsStore()

const events = ref([])
const loading = ref(true)
const search = ref('')
const pagination = ref({ page: 1, pages: 1, total: 0 })

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadEvents()
  }, 500)
}

const loadEvents = async (page = 1) => {
  loading.value = true
  try {
    const data = await eventsStore.fetchEvents({ 
      page, 
      search: search.value,
      upcoming: true 
    })
    events.value = data.events
    pagination.value = eventsStore.pagination
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  loadEvents(page)
}

onMounted(() => {
  loadEvents()
})
</script>
