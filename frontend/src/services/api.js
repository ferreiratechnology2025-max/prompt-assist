import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' }
})

export const templateApi = {
  list: () => apiClient.get('/templates'),
  get: (name) => apiClient.get(`/templates/${name}`),
  getSchema: (name) => apiClient.get(`/templates/${name}/schema`),
  generate: (data) => apiClient.post('/templates/generate', data)
}

export const validateApi = {
  validate: (prompt, originalGoal) =>
    apiClient.post('/validate', { prompt, original_goal: originalGoal })
}

export const memoryApi = {
  getStats: () => apiClient.get('/memory/stats'),
  getEntries: () => apiClient.get('/memory/entries')
}

export const healthApi = {
  check: () => apiClient.get('/health')
}
