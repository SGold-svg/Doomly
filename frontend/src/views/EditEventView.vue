<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">Create Event</h1>
      
      <form @submit.prevent="createEvent" class="card">
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {{ error }}
        </div>
        
        <div class="mb-6">
          <h2 class="text-lg font-semibold mb-4">Basic Information</h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="label">Event Title *</label>
              <input v-model="form.title" type="text" class="input" required>
            </div>
            <div class="col-span-2">
              <label class="label">Description</label>
              <textarea v-model="form.description" class="input" rows="4"></textarea>
            </div>
            <div>
              <label class="label">Event Type</label>
              <select v-model="form.event_type" class="input">
                <option value="">Select type</option>
                <option value="conference">Conference</option>
                <option value="workshop">Workshop</option>
                <option value="webinar">Webinar</option>
                <option value="concert">Concert</option>
                <option value="meetup">Meetup</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="label">Capacity</label>
              <input v-model.number="form.capacity" type="number" class="input" min="1">
            </div>
          </div>
        </div>
        
        <div class="mb-6">
          <h2 class="text-lg font-semibold mb-4">Date & Time</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Start Date *</label>
              <input v-model="form.start_date" type="datetime-local" class="input" required>
            </div>
            <div>
              <label class="label">End Date *</label>
              <input v-model="form.end_date" type="datetime-local" class="input" required>
            </div>
          </div>
        </div>
        
        <div class="mb-6">
          <h2 class="text-lg font-semibold mb-4">Location</h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="flex items-center">
                <input v-model="form.is_online" type="checkbox" class="mr-2">
                <span>This is an online event</span>
              </label>
            </div>
            <div v-if="!form.is_online">
              <label class="label">Venue Name</label>
              <input v-model="form.venue_name" type="text" class="input">
            </div>
            <div v-if="!form.is_online">
              <label class="label">City</label>
              <input v-model="form.city" type="text" class="input">
            </div>
            <div v-if="form.is_online">
              <label class="label">Online Link</label>
              <input v-model="form.online_link" type="url" class="input">
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-4">
          <router-link to="/dashboard/events" class="btn-secondary">Cancel</router-link>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Event' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEventsStore } from '@/stores/events'

const router = useRouter()
const eventsStore = useEventsStore()

const loading = ref(false)
const error = ref('')

const form = ref({
  title: '',
  description: '',
  event_type: '',
  capacity: null,
  start_date: '',
  end_date: '',
  is_online: false,
  venue_name: '',
  city: '',
  country: 'Belgium',
  online_link: '',
})

const createEvent = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const eventData = {
      ...form.value,
      start_date: new Date(form.value.start_date).toISOString(),
      end_date: new Date(form.value.end_date).toISOString(),
    }
    
    const event = await eventsStore.createEvent(eventData)
    router.push(`/dashboard/event/${event.id}/edit`)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to create event'
  } finally {
    loading.value = false
  }
}
</script>
