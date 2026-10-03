import { ref } from 'vue'
import { templateApi } from '../services/api'

const result = ref(null)
const loading = ref(false)
const error = ref(null)

export function useGeneration() {
  async function generate(templateName, fieldValues, userGoal, skipMemory = false) {
    loading.value = true
    error.value = null
    result.value = null

    try {
      const res = await templateApi.generate({
        template_name: templateName,
        field_values: fieldValues,
        user_goal: userGoal,
        skip_memory: skipMemory
      })
      result.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Erro ao gerar prompt'
    } finally {
      loading.value = false
    }
  }

  function clear() {
    result.value = null
    error.value = null
  }

  return { result, loading, error, generate, clear }
}
