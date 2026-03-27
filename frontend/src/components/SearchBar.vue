<template>
  <form class="search-bar" @submit.prevent="onSubmit">
    <input
      v-model="inputValue"
      type="text"
      placeholder="Pesquise qualquer coisa..."
      class="search-input"
      aria-label="Campo de busca"
    />
    <button type="submit" class="search-btn">Buscar</button>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  initialQuery: { type: String, default: '' },
})
const emit = defineEmits(['search'])
const inputValue = ref(props.initialQuery)

watch(() => props.initialQuery, (val) => { inputValue.value = val })

function onSubmit() {
  const q = inputValue.value.trim()
  if (q) emit('search', q)
}
</script>

<style scoped>
.search-bar { display: flex; gap: 0.5rem; margin: 1.5rem 0; }
.search-input { flex: 1; padding: 0.75rem 1rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 8px; outline: none; }
.search-input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }
.search-btn { padding: 0.75rem 1.5rem; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.search-btn:hover { background: #1d4ed8; }
</style>
