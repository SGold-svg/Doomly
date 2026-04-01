<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center">
              <span class="text-2xl font-bold text-doomly-600">D</span>
              <span class="text-2xl font-bold text-gray-900">oomly</span>
            </router-link>
            <div class="hidden md:flex ml-10 space-x-8">
              <router-link to="/events" class="text-gray-600 hover:text-doomly-600 px-3 py-2">Browse Events</router-link>
              <router-link to="/dashboard" class="text-gray-600 hover:text-doomly-600 px-3 py-2">Dashboard</router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <template v-if="!authStore.isAuthenticated">
              <router-link to="/login" class="text-gray-600 hover:text-doomly-600 px-3 py-2">Login</router-link>
              <router-link to="/register" class="btn-primary">Get Started</router-link>
            </template>
            <template v-else>
              <span class="text-gray-600">Welcome, {{ authStore.user?.first_name }}</span>
              <button @click="logout" class="text-gray-600 hover:text-doomly-600">Logout</button>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-doomly-600 to-indigo-600 text-white py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 class="text-5xl font-bold mb-4">Create Unforgettable Events</h1>
        <p class="text-xl text-doomly-100 mb-8">The all-in-one platform for event management, ticketing, and attendee engagement</p>
        <div class="flex justify-center gap-4">
          <router-link to="/register" class="bg-white text-doomly-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
            Start Free Trial
          </router-link>
          <router-link to="/events" class="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-doomly-600 transition">
            Browse Events
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-center mb-12">Everything You Need to Succeed</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="card text-center">
            <div class="text-4xl mb-4">🎫</div>
            <h3 class="text-xl font-semibold mb-2">Smart Ticketing</h3>
            <p class="text-gray-600">Multiple ticket types, promo codes, capacity management, and real-time sales tracking.</p>
          </div>
          <div class="card text-center">
            <div class="text-4xl mb-4">📊</div>
            <h3 class="text-xl font-semibold mb-2">Powerful Analytics</h3>
            <p class="text-gray-600">Track sales, attendance, revenue, and engagement with comprehensive dashboards.</p>
          </div>
          <div class="card text-center">
            <div class="text-4xl mb-4">📱</div>
            <h3 class="text-xl font-semibold mb-2">Easy Check-in</h3>
            <p class="text-gray-600">QR code scanning, badge printing, and instant attendee verification.</p>
          </div>
          <div class="card text-center">
            <div class="text-4xl mb-4">📧</div>
            <h3 class="text-xl font-semibold mb-2">Email Marketing</h3>
            <p class="text-gray-600">Automated confirmations, reminders, and custom email campaigns.</p>
          </div>
          <div class="card text-center">
            <div class="text-4xl mb-4">🎨</div>
            <h3 class="text-xl font-semibold mb-2">Beautiful Pages</h3>
            <p class="text-gray-600">Customizable event pages that look great on any device.</p>
          </div>
          <div class="card text-center">
            <div class="text-4xl mb-4">🔒</div>
            <h3 class="text-xl font-semibold mb-2">Secure Payments</h3>
            <p class="text-gray-600">PCI-compliant processing with multiple payment options.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Events -->
    <section class="py-20 bg-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold">Upcoming Events</h2>
          <router-link to="/events" class="text-doomly-600 hover:text-doomly-700">View All →</router-link>
        </div>
        <div v-if="loading" class="text-center py-12">Loading events...</div>
        <div v-else-if="events.length === 0" class="text-center py-12 text-gray-500">
          No upcoming events. Be the first to create one!
        </div>
        <div v-else class="grid md:grid-cols-3 gap-6">
          <EventCard v-for="event in events.slice(0, 6)" :key="event.id" :event="event" />
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-20 bg-doomly-600 text-white">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-4xl font-bold mb-4">Ready to Get Started?</h2>
        <p class="text-xl text-doomly-100 mb-8">Join thousands of organizers who trust Doomly for their events</p>
        <router-link to="/register" class="bg-white text-doomly-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
          Create Free Account
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import EventCard from '@/components/EventCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()

const events = ref([])
const loading = ref(true)

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(async () => {
  try {
    const data = await eventsStore.fetchEvents({ upcoming: true })
    events.value = data.events || []
  } finally {
    loading.value = false
  }
})
</script>
