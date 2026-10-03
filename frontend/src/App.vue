<template>
  <div class="app-layout">
    <Sidebar
      :templates="templates"
      :selected="selectedName"
      :loading="tplLoading"
      :error="tplError"
      :memoryStats="memoryStats"
      @select="onSelectTemplate"
    />

    <main class="main-content">
      <LoadingSpinner :visible="genLoading" message="Gerando prompt..." />

      <div class="content-area" v-if="!genLoading">
        <DynamicForm
          :template="selectedTemplate"
          @generate="onGenerate"
        />

        <PromptDisplay :prompt="genResult?.generated_prompt" />

        <ValidationScore
          v-if="genResult"
          :score="genResult.validation_score"
          :passed="genResult.passed_validation"
          :iterations="genResult.iterations_used"
          :validationResult="genResult.success ? genResult.validation_result : null"
        />

        <div v-if="genError" class="error-banner">{{ genError }}</div>

        <GenerationHistory
          :newEntry="genResult"
          @restore="onRestoreHistory"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import DynamicForm from './components/DynamicForm.vue'
import PromptDisplay from './components/PromptDisplay.vue'
import ValidationScore from './components/ValidationScore.vue'
import GenerationHistory from './components/GenerationHistory.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'
import { useTemplates } from './composables/useTemplates'
import { useGeneration } from './composables/useGeneration'

const {
  templates, selectedTemplate, loading: tplLoading,
  error: tplError, memoryStats, loadTemplates, selectTemplate, loadMemoryStats
} = useTemplates()

const { result: genResult, loading: genLoading, error: genError, generate } = useGeneration()

const selectedName = ref(null)

onMounted(() => {
  loadTemplates()
  loadMemoryStats()
})

async function onSelectTemplate(name) {
  selectedName.value = name
  await selectTemplate(name)
}

async function onGenerate({ fieldValues, userGoal, skipMemory }) {
  if (!selectedName.value) return
  await generate(selectedName.value, fieldValues, userGoal, skipMemory)
}

function onRestoreHistory(entry) {
  if (!entry.prompt) return
}
</script>

<style scoped>
.app-layout {
  display: flex; height: 100vh; overflow: hidden;
}
.main-content {
  flex: 1; overflow-y: auto; position: relative;
  background: #f8f9fa;
}
.content-area {
  max-width: 800px; margin: 0 auto; padding: 20px;
}
.error-banner {
  background: #fdecea; color: #e74c3c; padding: 12px 16px;
  border-radius: 8px; font-size: 13px; margin-top: 20px;
}
</style>
