import { defineStore } from 'pinia'
import api from '@/api'

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [],
    currentEvent: null,
    myEvents: [],
    loading: false,
    pagination: {
      page: 1,
      pages: 1,
      total: 0,
    },
  }),
  
  actions: {
    async fetchEvents(params = {}) {
      this.loading = true
      try {
        const { data } = await api.get('/events', { params })
        this.events = data.events
        this.pagination = {
          page: data.current_page,
          pages: data.pages,
          total: data.total,
        }
        return data
      } finally {
        this.loading = false
      }
    },
    
    async fetchEvent(slug) {
      this.loading = true
      try {
        const { data } = await api.get(`/events/${slug}`)
        this.currentEvent = data.event
        return data.event
      } finally {
        this.loading = false
      }
    },
    
    async fetchMyEvents(params = {}) {
      this.loading = true
      try {
        const { data } = await api.get('/events/my-events', { params })
        this.myEvents = data.events
        return data
      } finally {
        this.loading = false
      }
    },
    
    async createEvent(eventData) {
      const { data } = await api.post('/events', eventData)
      this.myEvents.unshift(data.event)
      return data.event
    },
    
    async updateEvent(eventId, eventData) {
      const { data } = await api.put(`/events/${eventId}`, eventData)
      const index = this.myEvents.findIndex(e => e.id === eventId)
      if (index !== -1) {
        this.myEvents[index] = data.event
      }
      return data.event
    },
    
    async deleteEvent(eventId) {
      await api.delete(`/events/${eventId}`)
      this.myEvents = this.myEvents.filter(e => e.id !== eventId)
    },
    
    async publishEvent(eventId) {
      const { data } = await api.post(`/events/${eventId}/publish`)
      return data.event
    },
  },
})
