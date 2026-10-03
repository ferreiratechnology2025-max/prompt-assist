<template>
  <div class="spinner-overlay" v-if="visible">
    <div class="spinner"></div>
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  message: { type: String, default: 'Carregando...' }
})
</script>

<style scoped>
.spinner-overlay {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  padding: 40px; color: #666;
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #e0e0e0; border-top-color: #4a90d9;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg) } }
</style>
