<template>
  <div class="card">
    <img v-if="event.banner" :src="event.banner" :alt="event.title" class="w-full h-48 object-cover rounded-lg mb-4">
    <div v-else class="w-full h-48 bg-gradient-to-r from-doomly-400 to-indigo-400 rounded-lg mb-4 flex items-center justify-center">
      <span class="text-white text-4xl">🎫</span>
    </div>
    <div class="text-sm text-doomly-600 mb-2">
      {{ formatDate(event.start_date) }}
      <span v-if="event.city"> • {{ event.city }}</span>
    </div>
    <h3 class="text-xl font-semibold mb-2 line-clamp-2">
      <router-link :to="`/event/${event.slug}`" class="hover:text-doomly-600">
        {{ event.title }}
      </router-link>
    </h3>
    <p v-if="event.summary" class="text-gray-600 text-sm line-clamp-2 mb-4">
      {{ event.summary }}
    </p>
    <div class="flex justify-between items-center">
      <span class="text-sm text-gray-500">
        {{ event.tickets?.length ? `From €${Math.min(...event.tickets.map(t => t.price || 0)).toFixed(2)}` : 'Free' }}
      </span>
      <router-link :to="`/event/${event.slug}`" class="text-doomly-600 hover:text-doomly-700 text-sm font-medium">
        View Details →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { format } from 'date-fns'

defineProps({
  event: {
    type: Object,
    required: true,
  },
})

const formatDate = (dateStr) => {
  return format(new Date(dateStr), 'EEE, MMM d, yyyy')
}
</script>
