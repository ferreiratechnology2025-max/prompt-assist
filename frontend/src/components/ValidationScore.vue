<template>
  <div class="validation-score" v-if="score !== null">
    <div class="score-header">
      <div class="score-circle" :style="{ '--score': score }">
        <svg viewBox="0 0 100 100" class="score-ring">
          <circle class="bg" cx="50" cy="50" r="42" />
          <circle
            class="fg"
            :class="colorClass"
            cx="50" cy="50" r="42"
            :style="{ strokeDashoffset: 264 - (264 * score) / 100 }"
          />
        </svg>
        <div class="score-value">{{ Math.round(score) }}</div>
      </div>
      <div class="score-meta">
        <div class="score-label" :class="colorClass">{{ label }}</div>
        <div class="score-sub" v-if="iterations">{{ iterations }} iteracao(oes)</div>
        <div class="score-pass" v-if="passed !== null">
          {{ passed ? 'Aprovado' : 'Nao aprovado' }}
        </div>
      </div>
    </div>

    <button v-if="checks.length" class="toggle-details" @click="showDetails = !showDetails">
      {{ showDetails ? 'Ocultar detalhes' : 'Ver detalhes' }}
    </button>

    <div v-if="showDetails && checks.length" class="details-panel">
      <div
        v-for="check in checks"
        :key="check.name"
        class="check-row"
      >
        <div class="check-header">
          <span class="check-name">{{ checkName(check.name) }}</span>
          <span class="check-score" :class="scoreColor(check.score)">
            {{ Math.round(check.score) }}
          </span>
          <span class="check-status" :class="check.passed ? 'pass' : 'fail'">
            {{ check.passed ? 'OK' : 'X' }}
          </span>
        </div>
        <div class="check-detail" v-if="check.details">{{ check.details }}</div>
      </div>
    </div>

    <div v-if="showDetails && suggestions.length" class="suggestions">
      <h4>Sugestoes de melhoria</h4>
      <ul>
        <li v-for="(s, i) in suggestions" :key="i">{{ s }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: null },
  passed: { type: Boolean, default: null },
  iterations: { type: Number, default: null },
  validationResult: { type: Object, default: null }
})

const showDetails = ref(false)

const checks = computed(() => {
  const r = props.validationResult
  if (!r?.checks) return []
  return Object.values(r.checks)
})

const suggestions = computed(() => {
  return props.validationResult?.suggested_fixes || []
})

const label = computed(() => {
  const s = props.score
  if (s === null || s === undefined) return ''
  if (s >= 85) return 'Excelente'
  if (s >= 70) return 'Bom'
  if (s >= 50) return 'Regular'
  return 'Insuficiente'
})

const colorClass = computed(() => {
  const s = props.score
  if (s >= 85) return 'green'
  if (s >= 70) return 'yellow'
  return 'red'
})

function scoreColor(s) {
  if (s >= 85) return 'green'
  if (s >= 70) return 'yellow'
  return 'red'
}

function checkName(name) {
  const map = { estrutura: 'Estrutura', ambiguidade: 'Ambiguidade', semantica: 'Semantica', restricoes: 'Restricoes', smart: 'SMART' }
  return map[name] || name
}
</script>

<style scoped>
.validation-score {
  background: #fff; border: 1px solid #eee; border-radius: 10px;
  padding: 20px; margin-top: 20px;
}
.score-header { display: flex; align-items: center; gap: 20px; }
.score-circle {
  position: relative; width: 80px; height: 80px; flex-shrink: 0;
}
.score-ring { width: 100%; height: 100%; transform: rotate(-90deg); }
.score-ring .bg { fill: none; stroke: #eee; stroke-width: 8; }
.score-ring .fg {
  fill: none; stroke-width: 8; stroke-linecap: round;
  stroke-dasharray: 264; transition: stroke-dashoffset 0.5s ease;
}
.score-ring .fg.green { stroke: #27ae60; }
.score-ring .fg.yellow { stroke: #f39c12; }
.score-ring .fg.red { stroke: #e74c3c; }
.score-value {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 24px; font-weight: 700; color: #333;
}
.score-meta { flex: 1; }
.score-label { font-size: 16px; font-weight: 600; }
.score-label.green { color: #27ae60; }
.score-label.yellow { color: #f39c12; }
.score-label.red { color: #e74c3c; }
.score-sub { font-size: 12px; color: #888; margin-top: 4px; }
.score-pass { font-size: 13px; font-weight: 500; margin-top: 4px; }
.toggle-details {
  margin-top: 16px; background: none; border: 1px solid #ddd;
  padding: 6px 14px; border-radius: 6px; cursor: pointer;
  font-size: 13px; color: #666;
}
.details-panel { margin-top: 12px; border-top: 1px solid #eee; padding-top: 12px; }
.check-row { padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.check-header {
  display: flex; align-items: center; gap: 8px;
}
.check-name { flex: 1; font-size: 13px; font-weight: 500; color: #555; }
.check-score { font-size: 14px; font-weight: 600; }
.check-score.green { color: #27ae60; }
.check-score.yellow { color: #f39c12; }
.check-score.red { color: #e74c3c; }
.check-status { font-size: 11px; padding: 2px 6px; border-radius: 4px; }
.check-status.pass { background: #e8f5e9; color: #27ae60; }
.check-status.fail { background: #fdecea; color: #e74c3c; }
.check-detail { font-size: 12px; color: #888; margin-top: 4px; }
.suggestions { margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee; }
.suggestions h4 { margin: 0 0 8px; font-size: 13px; color: #333; }
.suggestions ul { margin: 0; padding-left: 20px; }
.suggestions li { font-size: 12px; color: #666; margin-bottom: 4px; }
</style>
