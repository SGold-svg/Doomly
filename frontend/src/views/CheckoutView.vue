<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <h1 class="text-3xl font-bold mb-8">Checkout</h1>
      
      <div v-if="loading" class="text-center py-12">Loading...</div>
      <div v-else-if="event" class="grid lg:grid-cols-2 gap-8">
        <!-- Order Form -->
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">Your Information</h2>
          <form @submit.prevent="placeOrder">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="label">First Name</label>
                <input v-model="form.first_name" type="text" class="input" required>
              </div>
              <div>
                <label class="label">Last Name</label>
                <input v-model="form.last_name" type="text" class="input" required>
              </div>
            </div>
            <div class="mb-4">
              <label class="label">Email</label>
              <input v-model="form.email" type="email" class="input" required>
            </div>
            
            <h3 class="text-lg font-semibold mt-6 mb-4">Tickets</h3>
            <div v-for="ticket in availableTickets" :key="ticket.id" class="flex justify-between items-center p-3 bg-gray-50 rounded mb-2">
              <div>
                <span class="font-medium">{{ ticket.name }}</span>
                <span class="text-sm text-gray-500 ml-2">€{{ ticket.price }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button type="button" @click="decrementTicket(ticket)" class="w-8 h-8 rounded bg-gray-200">-</button>
                <span>{{ getTicketQuantity(ticket.id) }}</span>
                <button type="button" @click="incrementTicket(ticket)" class="w-8 h-8 rounded bg-gray-200">+</button>
              </div>
            </div>
            
            <div v-if="totalQuantity > 0" class="mt-6 pt-4 border-t">
              <div class="flex justify-between mb-2">
                <span>Subtotal</span>
                <span>€{{ subtotal.toFixed(2) }}</span>
              </div>
              <div v-if="discount > 0" class="flex justify-between mb-2 text-green-600">
                <span>Discount</span>
                <span>-€{{ discount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>€{{ total.toFixed(2) }}</span>
              </div>
              
              <button type="submit" class="btn-primary w-full mt-4" :disabled="processing">
                {{ processing ? 'Processing...' : 'Place Order' }}
              </button>
            </div>
          </form>
        </div>
        
        <!-- Event Summary -->
        <div class="card">
          <h2 class="text-xl font-semibold mb-4">{{ event.title }}</h2>
          <p class="text-gray-600 mb-4">{{ formatDate(event.start_date) }}</p>
          <p v-if="event.location?.venue_name" class="text-gray-600 mb-4">{{ event.location.venue_name }}</p>
          <p v-if="event.description" class="text-gray-600">{{ event.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from '@/stores/events'
import api from '@/api'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()
const eventsStore = useEventsStore()

const event = ref(null)
const loading = ref(true)
const processing = ref(false)
const cart = ref({})
const promoCode = ref('')
const discount = ref(0)

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
})

const availableTickets = computed(() => {
  return event.value?.tickets?.filter(t => t.is_available && !t.is_hidden) || []
})

const totalQuantity = computed(() => {
  return Object.values(cart.value).reduce((sum, qty) => sum + qty, 0)
})

const subtotal = computed(() => {
  return availableTickets.value.reduce((sum, ticket) => {
    return sum + (ticket.price * (cart.value[ticket.id] || 0))
  }, 0)
})

const total = computed(() => {
  return subtotal.value - discount.value
})

const getTicketQuantity = (ticketId) => cart.value[ticketId] || 0

const incrementTicket = (ticket) => {
  const current = cart.value[ticket.id] || 0
  if (current < Math.min(ticket.max_per_order, ticket.quantity_remaining)) {
    cart.value[ticket.id] = current + 1
  }
}

const decrementTicket = (ticket) => {
  const current = cart.value[ticket.id] || 0
  if (current > 0) {
    cart.value[ticket.id] = current - 1
  }
}

const formatDate = (dateStr) => format(new Date(dateStr), 'EEEE, MMMM d, yyyy')

const placeOrder = async () => {
  if (totalQuantity.value === 0) return
  
  processing.value = true
  try {
    const items = Object.entries(cart.value)
      .filter(([_, qty]) => qty > 0)
      .map(([ticket_id, quantity]) => ({ ticket_type_id: parseInt(ticket_id), quantity }))
    
    const { data } = await api.post('/orders', {
      event_id: event.value.id,
      items,
      ...form.value
    })
    
    router.push(`/order/${data.order.order_number}`)
  } catch (error) {
    alert(error.response?.data?.error || 'Order failed')
  } finally {
    processing.value = false
  }
}

onMounted(async () => {
  try {
    event.value = await eventsStore.fetchEvent(route.params.eventSlug)
  } finally {
    loading.value = false
  }
})
</script>
