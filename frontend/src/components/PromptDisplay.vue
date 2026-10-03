<template>
  <div class="prompt-display" v-if="prompt">
    <div class="prompt-toolbar">
      <span class="prompt-label">Prompt gerado</span>
      <div class="toolbar-actions">
        <button @click="copyPrompt" class="btn-small" :title="copied ? 'Copiado!' : 'Copiar'">
          {{ copied ? 'Copiado' : 'Copiar' }}
        </button>
        <button @click="downloadPrompt" class="btn-small">Download .txt</button>
      </div>
    </div>
    <pre class="prompt-content"><code>{{ prompt }}</code></pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  prompt: { type: String, default: null }
})

const copied = ref(false)

function copyPrompt() {
  if (!props.prompt) return
  navigator.clipboard.writeText(props.prompt)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function downloadPrompt() {
  if (!props.prompt) return
  const blob = new Blob([props.prompt], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'prompt.txt'; a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.prompt-display {
  background: #1e1e2e; border-radius: 10px; overflow: hidden; margin-top: 20px;
}
.prompt-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 16px; background: #2a2a3e;
}
.prompt-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.toolbar-actions { display: flex; gap: 8px; }
.btn-small {
  padding: 4px 12px; background: #3a3a4e; color: #ccc;
  border: 1px solid #4a4a5e; border-radius: 4px;
  font-size: 12px; cursor: pointer;
}
.btn-small:hover { background: #4a4a5e; }
.prompt-content {
  margin: 0; padding: 20px; overflow-x: auto;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px; line-height: 1.5; color: #d4d4d4;
  white-space: pre-wrap; word-break: break-word;
}
</style>
