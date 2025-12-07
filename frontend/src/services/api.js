import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchDatasets = async (query, topK = 5) => {
  try {
    const response = await api.post('/query/', {
      query,
      top_k: topK
    })
    return response.data
  } catch (error) {
    console.error('Search error:', error)
    throw error
  }
}

export const generateWorkflow = async (datasetUrl, format, variable, title) => {
  try {
    const response = await api.post('/workflow/generate', {
      dataset_url: datasetUrl,
      dataset_format: format,
      variable: variable,
      title: title || 'Generated Workflow'
    })
    return response.data
  } catch (error) {
    console.error('Workflow generation error:', error)
    throw error
  }
}

export const checkHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check error:', error)
    throw error
  }
}

export default api
