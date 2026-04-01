import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/views/EventsView.vue'),
  },
  {
    path: '/event/:slug',
    name: 'EventDetail',
    component: () => import('@/views/EventDetailView.vue'),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/events',
    name: 'MyEvents',
    component: () => import('@/views/MyEventsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/event/:id/edit',
    name: 'EditEvent',
    component: () => import('@/views/EditEventView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/orders',
    name: 'Orders',
    component: () => import('@/views/OrdersView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/attendees/:eventId',
    name: 'Attendees',
    component: () => import('@/views/AttendeesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard/checkin/:eventId',
    name: 'CheckIn',
    component: () => import('@/views/CheckInView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/checkout/:eventSlug',
    name: 'Checkout',
    component: () => import('@/views/CheckoutView.vue'),
  },
  {
    path: '/order/:orderNumber',
    name: 'OrderConfirmation',
    component: () => import('@/views/OrderConfirmationView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
