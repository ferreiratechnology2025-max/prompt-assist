<template>
  <div class="history" v-if="entries.length">
    <h4>Historico</h4>
    <div
      v-for="(entry, i) in entries"
      :key="i"
      class="history-item"
      @click="$emit('restore', entry)"
    >
      <span class="h-template">{{ entry.template }}</span>
      <span class="h-score" :class="scoreClass(entry.score)">{{ Math.round(entry.score) }}</span>
      <span class="h-time">{{ entry.time }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  newEntry: { type: Object, default: null }
})

defineEmits(['restore'])

const STORAGE_KEY = 'qualiprompt_history'
const entries = ref(loadHistory())

watch(() => props.newEntry, (entry) => {
  if (!entry) return
  entries.value.unshift({
    template: entry.template_name || entry.template,
    score: entry.validation_score || 0,
    prompt: entry.generated_prompt || '',
    time: new Date().toLocaleTimeString()
  })
  if (entries.value.length > 10) entries.value.pop()
  saveHistory(entries.value)
})

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch { return [] }
}

function saveHistory(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

function scoreClass(s) {
  if (s >= 85) return 'green'
  if (s >= 70) return 'yellow'
  return 'red'
}
</script>

<style scoped>
.history { margin-top: 24px; }
.history h4 { margin: 0 0 8px; font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.history-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; cursor: pointer; border-radius: 6px;
  font-size: 12px; color: #666; transition: background 0.15s;
}
.history-item:hover { background: #f5f5f5; }
.h-template { flex: 1; }
.h-score { font-weight: 600; }
.h-score.green { color: #27ae60; }
.h-score.yellow { color: #f39c12; }
.h-score.red { color: #e74c3c; }
.h-time { font-size: 11px; color: #aaa; }
</style>
