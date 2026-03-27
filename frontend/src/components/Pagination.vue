<template>
  <div class="pagination">
    <button @click="$emit('prev')" :disabled="currentPage <= 1" class="page-btn">← Anterior</button>
    <span class="page-num">Página {{ currentPage }}</span>
    <button @click="$emit('next')" :disabled="!hasNext" class="page-btn">Próxima →</button>
  </div>
</template>

<script setup>
defineProps({
  currentPage: { type: Number, required: true },
  hasNext: { type: Boolean, required: true },
})
defineEmits(['prev', 'next'])
</script>

<style scoped>
.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 2rem; }
.page-btn { padding: 0.5rem 1.25rem; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95rem; }
.page-btn:disabled { background: #ccc; cursor: not-allowed; }
.page-num { font-weight: bold; color: #333; }
</style>
