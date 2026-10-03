<template>
  <div class="dynamic-form">
    <h3>{{ template?.assistant_role || 'Template' }}</h3>

    <div v-if="!template" class="empty-state">
      Selecione um template na sidebar para comecar.
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <div class="field-group">
        <label v-for="field in template.required_fields" :key="field.name">
          <span class="label-text">{{ field.question }} <span class="required">*</span></span>
          <input
            v-if="field.type === 'text'"
            v-model="formValues[field.name]"
            :placeholder="field.question"
            required
          />
          <textarea
            v-else
            v-model="formValues[field.name]"
            :placeholder="field.question"
            rows="3"
            required
          ></textarea>
        </label>
      </div>

      <div class="field-group">
        <label>
          <span class="label-text">Objetivo / Instrucao extra</span>
          <textarea
            v-model="userGoal"
            placeholder="Descreva o objetivo especifico do prompt..."
            rows="2"
          ></textarea>
        </label>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="!isValid">
          Gerar Prompt
        </button>
        <label class="skip-mem">
          <input type="checkbox" v-model="skipMemory" />
          Ignorar memoria
        </label>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
  template: { type: Object, default: null }
})

const emit = defineEmits(['generate'])

const formValues = reactive({})
const userGoal = ref('')
const skipMemory = ref(false)

watch(() => props.template, (tpl) => {
  Object.keys(formValues).forEach(k => delete formValues[k])
  userGoal.value = ''
  if (tpl?.required_fields) {
    tpl.required_fields.forEach(f => { formValues[f.name] = '' })
  }
}, { immediate: true })

const isValid = computed(() => {
  if (!props.template?.required_fields) return false
  return props.template.required_fields.every(f => formValues[f.name]?.trim())
})

function handleSubmit() {
  if (!isValid.value) return
  const values = {}
  Object.keys(formValues).forEach(k => { values[k] = formValues[k] })
  emit('generate', {
    fieldValues: values,
    userGoal: userGoal.value,
    skipMemory: skipMemory.value
  })
}
</script>

<style scoped>
.dynamic-form {
  padding: 20px; max-width: 680px;
}
.dynamic-form h3 { margin: 0 0 20px; color: #333; font-size: 16px; }
.empty-state {
  padding: 60px 20px; text-align: center; color: #999; font-size: 14px;
}
.field-group { margin-bottom: 16px; }
.field-group label {
  display: block; margin-bottom: 12px;
}
.label-text {
  display: block; margin-bottom: 4px; font-size: 13px; color: #555; font-weight: 600;
}
.required { color: #e74c3c; }
input, textarea {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ddd; border-radius: 6px;
  font-size: 14px; color: #333; outline: none;
  box-sizing: border-box; font-family: inherit;
}
input:focus, textarea:focus { border-color: #4a90d9; box-shadow: 0 0 0 2px rgba(74,144,217,0.15); }
.form-actions {
  display: flex; align-items: center; gap: 16px; margin-top: 24px;
}
.btn-primary {
  padding: 10px 24px; background: #4a90d9; color: #fff;
  border: none; border-radius: 6px; font-size: 14px; cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: #357abd; }
.btn-primary:disabled { background: #aaa; cursor: not-allowed; }
.skip-mem { font-size: 12px; color: #888; cursor: pointer; display: flex; align-items: center; gap: 4px; }
</style>
