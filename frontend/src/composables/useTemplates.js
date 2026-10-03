import { ref, computed } from 'vue'
import { templateApi, memoryApi } from '../services/api'

const templates = ref([])
const selectedTemplate = ref(null)
const loading = ref(false)
const error = ref(null)
const memoryStats = ref(null)

export function useTemplates() {
  async function loadTemplates() {
    loading.value = true
    error.value = null
    try {
      const res = await templateApi.list()
      templates.value = res.data.templates
    } catch (e) {
      error.value = e.response?.data?.detail || 'Erro ao carregar templates'
    } finally {
      loading.value = false
    }
  }

  async function selectTemplate(name) {
    loading.value = true
    error.value = null
    try {
      const res = await templateApi.get(name)
      selectedTemplate.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Erro ao selecionar template'
    } finally {
      loading.value = false
    }
  }

  async function loadMemoryStats() {
    try {
      const res = await memoryApi.getStats()
      memoryStats.value = res.data
    } catch {
      memoryStats.value = null
    }
  }

  return {
    templates,
    selectedTemplate,
    loading,
    error,
    memoryStats,
    loadTemplates,
    selectTemplate,
    loadMemoryStats
  }
}
