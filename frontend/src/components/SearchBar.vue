<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['search'])

const inputValue = ref('')

function submit() {
  const q = inputValue.value.trim()
  if (q) emit('search', q)
}
</script>

<template>
  <form class="search-bar" role="search" @submit.prevent="submit">
    <input
      v-model="inputValue"
      class="search-bar__input"
      type="search"
      placeholder="Digite sua pesquisa…"
      aria-label="Campo de pesquisa"
      :disabled="loading"
      autofocus
    />
    <button
      class="search-bar__btn"
      type="submit"
      :disabled="loading || !inputValue.trim()"
      aria-label="Pesquisar"
    >
      <span v-if="loading" class="spinner" aria-hidden="true" />
      <span v-else>Buscar</span>
    </button>
  </form>
</template>

<style scoped>
.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.search-bar__input {
  flex: 1;
  padding: 0.65rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: var(--color-surface);
  color: var(--color-text);
}

.search-bar__input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.search-bar__input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-bar__btn {
  padding: 0.65rem 1.5rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 5.5rem;
}

.search-bar__btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.search-bar__btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 1.1rem;
  height: 1.1rem;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
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
