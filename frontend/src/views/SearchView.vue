<template>
  <div class="search-view">
    <SearchBar :initial-query="query" @search="onSearch" />

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="loading" class="loading">Buscando...</div>

    <div v-if="results.length > 0 && !loading">
      <div class="meta">
        <span>{{ totalResults }} resultado(s) — página {{ currentPage }}</span>
        <span class="limit-info">Buscas hoje: {{ searchesToday }} / {{ searchesLimit }}</span>
      </div>

      <ResultCard
        v-for="(result, i) in results"
        :key="i"
        :result="result"
      />

      <Pagination
        :current-page="currentPage"
        :has-next="hasNext"
        @prev="goToPage(currentPage - 1)"
        @next="goToPage(currentPage + 1)"
      />
    </div>

    <div v-if="!loading && results.length === 0 && query" class="no-results">
      Nenhum resultado encontrado para <strong>"{{ query }}"</strong>.
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchAPI } from '../api'
import SearchBar from '../components/SearchBar.vue'
import ResultCard from '../components/ResultCard.vue'
import Pagination from '../components/Pagination.vue'

const route = useRoute()
const router = useRouter()
const query = ref(route.query.q || '')
const results = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(Number(route.query.page) || 1)
const totalResults = ref(0)
const searchesToday = ref(0)
const searchesLimit = ref(50)
const hasNext = ref(false)
const PER_PAGE = 10

async function doSearch() {
  if (!query.value) return
  loading.value = true
  error.value = ''
  results.value = []
  try {
    const resp = await searchAPI.search(query.value, currentPage.value, PER_PAGE)
    results.value = resp.data.results
    totalResults.value = resp.data.total
    searchesToday.value = resp.data.searches_today
    searchesLimit.value = resp.data.searches_today + resp.data.searches_remaining
    hasNext.value = resp.data.results.length >= PER_PAGE
  } catch (err) {
    if (err.response?.status === 429) {
      error.value = 'Limite diário de buscas atingido. Tente novamente amanhã.'
    } else {
      error.value = 'Erro ao realizar a busca. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}

function onSearch(q) {
  query.value = q
  currentPage.value = 1
  router.push({ path: '/search', query: { q, page: 1 } })
}

function goToPage(page) {
  currentPage.value = page
  router.push({ path: '/search', query: { q: query.value, page } })
}

watch(() => route.query, () => {
  query.value = route.query.q || ''
  currentPage.value = Number(route.query.page) || 1
  doSearch()
}, { immediate: false })

onMounted(() => {
  if (query.value) doSearch()
})
</script>

<style scoped>
.meta { display: flex; justify-content: space-between; margin: 1rem 0; color: #666; font-size: 0.9rem; }
.loading, .no-results { text-align: center; padding: 2rem; color: #666; }
.error { background: #fee; border: 1px solid #fcc; padding: 1rem; border-radius: 8px; margin: 1rem 0; color: #c00; }
.limit-info { font-size: 0.85rem; }
</style>
