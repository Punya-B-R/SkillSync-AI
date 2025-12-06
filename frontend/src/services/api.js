/**
 * API service for communicating with backend.
 */
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds (2 minutes) for AI calls
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response:`, response.status, response.data)
    return response
  },
  (error) => {
    console.error('[API] Response error:', error.response?.data || error.message)
    
    // Handle common errors
    if (error.response) {
      const { status, data } = error.response
      const message = data?.message || 'An error occurred'
      
      if (status === 401) {
        console.error('[API] Authentication error')
      } else if (status === 403) {
        console.error('[API] Forbidden')
      } else if (status === 404) {
        console.error('[API] Not found')
      } else if (status === 500) {
        console.error('[API] Server error')
      } else if (status === 504) {
        console.error('[API] Timeout - request took too long')
      }
      
      return Promise.reject({
        message,
        status,
        data: data || {},
      })
    }
    
    // Handle timeout errors specifically
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return Promise.reject({
        message: 'Request timed out. The AI is taking longer than expected. Please try again.',
        status: 0,
      })
    }
    
    return Promise.reject({
      message: error.message || 'Network error. Please check your connection.',
      status: 0,
    })
  }
)

// Export API methods
export const apiService = {
  uploadResume: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  analyzeResume: (resumeText) =>
    api.post('/analyze-resume', { resume_text: resumeText }),

  recommendDomains: (profile) =>
    api.post('/recommend-domains', { profile }),

  generateRoadmap: (userData) =>
    api.post('/generate-roadmap', userData),

  chat: (message, context) =>
    api.post('/chat', { message, context }),
}

// Legacy exports for backward compatibility
export const uploadResume = async (file) => {
  const response = await apiService.uploadResume(file)
  return response.data
}

export const analyzeResume = async (resumeText) => {
  const response = await apiService.analyzeResume(resumeText)
  return response.data
}

export const recommendDomains = async (profile) => {
  const response = await apiService.recommendDomains(profile)
  return response.data
}

export const generateRoadmap = async (userData) => {
  const response = await apiService.generateRoadmap(userData)
  return response.data
}

export const chatWithAI = async (message, context = null) => {
  const response = await apiService.chat(message, context)
  return response.data
}

export default apiService

