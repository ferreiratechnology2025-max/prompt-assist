<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>QualiPrompt</h2>
      <span class="version">v0.3</span>
    </div>

    <div class="search-box">
      <input v-model="search" type="text" placeholder="Buscar template..." />
    </div>

    <nav class="template-list">
      <div v-if="loading" class="status-text">Carregando...</div>
      <div v-else-if="error" class="status-text error">{{ error }}</div>
      <button
        v-for="t in filteredTemplates"
        :key="t.name"
        :class="['template-item', { active: selected === t.name }]"
        @click="$emit('select', t.name)"
      >
        <span class="name">{{ t.name }}</span>
        <span class="ver">v{{ t.version || '1.0' }}</span>
      </button>
      <div v-if="!loading && filteredTemplates.length === 0" class="status-text">
        Nenhum template encontrado
      </div>
    </nav>

    <div class="memory-badge" v-if="memoryStats">
      <span class="dot"></span>
      Memoria: {{ memoryStats.total_entries }} entradas
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  templates: { type: Array, default: () => [] },
  selected: { type: String, default: null },
  loading: Boolean,
  error: String,
  memoryStats: { type: Object, default: null }
})

defineEmits(['select'])

const search = ref('')

const filteredTemplates = computed(() => {
  if (!search.value) return props.templates
  const q = search.value.toLowerCase()
  return props.templates.filter(t => t.name.toLowerCase().includes(q))
})
</script>

<style scoped>
.sidebar {
  width: 280px; min-width: 280px;
  background: #1a1a2e; color: #ccc;
  display: flex; flex-direction: column;
  height: 100vh; border-right: 1px solid #2a2a3e;
}
.sidebar-header {
  display: flex; align-items: center; gap: 8px;
  padding: 20px; border-bottom: 1px solid #2a2a3e;
}
.sidebar-header h2 { margin: 0; font-size: 18px; color: #fff; }
.version { font-size: 11px; color: #888; background: #2a2a3e; padding: 2px 6px; border-radius: 4px; }
.search-box { padding: 12px 16px; }
.search-box input {
  width: 100%; padding: 8px 12px;
  background: #2a2a3e; border: 1px solid #3a3a4e;
  border-radius: 6px; color: #ccc; font-size: 13px;
  outline: none; box-sizing: border-box;
}
.search-box input:focus { border-color: #4a90d9; }
.template-list { flex: 1; overflow-y: auto; padding: 0 8px; }
.template-item {
  display: flex; justify-content: space-between; align-items: center;
  width: 100%; padding: 10px 12px; margin-bottom: 2px;
  background: none; border: none; border-radius: 6px;
  color: #ccc; cursor: pointer; text-align: left; font-size: 13px;
  transition: background 0.15s;
}
.template-item:hover { background: #2a2a3e; }
.template-item.active { background: #4a90d9; color: #fff; }
.template-item .ver { font-size: 11px; opacity: 0.6; }
.status-text { padding: 20px; text-align: center; font-size: 13px; color: #888; }
.status-text.error { color: #e74c3c; }
.memory-badge {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 20px; border-top: 1px solid #2a2a3e;
  font-size: 12px; color: #888;
}
.memory-badge .dot {
  width: 8px; height: 8px; border-radius: 50%; background: #27ae60;
}
</style>
