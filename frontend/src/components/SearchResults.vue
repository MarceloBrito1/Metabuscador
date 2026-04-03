<script setup>
import ResultCard from './ResultCard.vue'

defineProps({
  results: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  searched: {
    type: Boolean,
    default: false,
  },
  query: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <section aria-label="Resultados da busca">
    <div v-if="loading" class="state-msg" aria-live="polite">
      <span class="spinner-lg" aria-hidden="true" />
      <p>Buscando resultados…</p>
    </div>

    <template v-else>
      <p v-if="searched && results.length === 0" class="state-msg state-msg--empty">
        Nenhum resultado encontrado para <strong>"{{ query }}"</strong>.
      </p>

      <p v-if="results.length > 0" class="results-count">
        {{ results.length }} resultado(s) encontrado(s)
      </p>

      <ul v-if="results.length > 0" class="results-list">
        <li v-for="(result, idx) in results" :key="idx">
          <ResultCard :result="result" />
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.results-count {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}

.results-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.state-msg {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.state-msg--empty {
  font-size: 0.95rem;
}

.spinner-lg {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
