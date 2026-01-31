import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const videoAPI = {
  // Process video
  processVideo: async (url) => {
    const response = await api.post('/process-video', { url })
    return response.data
  },

  // Get processing status
  getStatus: async () => {
    const response = await api.get('/process-status')
    return response.data
  },

  // Basic search
  basicSearch: async (query) => {
    const response = await api.post(`/intent-search?query=${encodeURIComponent(query)}`)
    return response.data
  },

  // RAG search
  ragSearch: async (query) => {
    const response = await api.post(`/rag-search?query=${encodeURIComponent(query)}`)
    return response.data
  },
}

export default api

