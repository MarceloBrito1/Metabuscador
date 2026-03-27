<template>
  <div class="home">
    <h1>🔍 Metabuscador</h1>
    <p>Um meta-buscador que agrega resultados de múltiplos motores de busca.</p>
    <SearchBar @search="onSearch" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'

const router = useRouter()

function onSearch(q) {
  router.push({ path: '/search', query: { q } })
}
</script>

<style scoped>
.home { text-align: center; padding: 4rem 1rem; }
.home h1 { font-size: 3rem; margin-bottom: 1rem; }
.home p { color: #666; margin-bottom: 2rem; font-size: 1.1rem; }
</style>
