<script setup>
import { ref, computed } from 'vue'
import SearchBar from './components/SearchBar.vue'
import SearchResults from './components/SearchResults.vue'

const query = ref('')
const results = ref([])
const isLoading = ref(false)
const error = ref(null)
const searched = ref(false)
const activeSource = ref('all')

const API_BASE = import.meta.env.VITE_API_URL || ''

const sources = computed(() => {
  const set = new Set(results.value.map((r) => r.source))
  return ['all', ...set]
})

const filteredResults = computed(() => {
  if (activeSource.value === 'all') return results.value
  return results.value.filter((r) => r.source === activeSource.value)
})

async function handleSearch(q) {
  if (!q.trim()) return
  query.value = q.trim()
  isLoading.value = true
  error.value = null
  searched.value = true
  results.value = []

  try {
    const url = `${API_BASE}/search?q=${encodeURIComponent(query.value)}&max_results=8`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    results.value = data.results
    activeSource.value = 'all'
  } catch (e) {
    error.value = 'Não foi possível realizar a busca. Verifique sua conexão e tente novamente.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header__inner">
        <h1 class="header__title">🔍 Metabuscador</h1>
        <p class="header__subtitle">Pesquise em múltiplas fontes de uma só vez</p>
      </div>
    </header>

    <main class="main">
      <SearchBar :loading="isLoading" @search="handleSearch" />

      <div v-if="error" class="alert alert--error" role="alert">
        {{ error }}
      </div>

      <div v-if="searched && !isLoading && !error" class="filter-bar">
        <span class="filter-bar__label">Filtrar por fonte:</span>
        <button
          v-for="src in sources"
          :key="src"
          class="filter-btn"
          :class="{ 'filter-btn--active': activeSource === src }"
          @click="activeSource = src"
        >
          {{ src === 'all' ? 'Todas' : src }}
        </button>
      </div>

      <SearchResults
        :results="filteredResults"
        :loading="isLoading"
        :searched="searched"
        :query="query"
      />
    </main>

    <footer class="footer">
      <p>Metabuscador &copy; {{ new Date().getFullYear() }}</p>
    </footer>
  </div>
</template>

<style>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow);
  padding: 2rem 1rem;
  text-align: center;
}

.header__title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.header__subtitle {
  margin-top: 0.25rem;
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

.main {
  flex: 1;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
  padding: 2rem 1rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.alert--error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: var(--color-error);
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.filter-bar__label {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.filter-btn {
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s;
}

.filter-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.footer {
  text-align: center;
  padding: 1rem;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  border-top: 1px solid var(--color-border);
}
</style>
