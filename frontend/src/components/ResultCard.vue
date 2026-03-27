<template>
  <div class="result-card">
    <span class="source">{{ result.source }}</span>
    <h3>
      <a :href="result.url" target="_blank" rel="noopener noreferrer">{{ result.title }}</a>
    </h3>
    <p class="url">{{ result.url }}</p>
    <p class="snippet">{{ result.snippet }}</p>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.result-card { background: white; padding: 1rem 1.25rem; margin-bottom: 0.75rem; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.source { font-size: 0.75rem; color: #2563eb; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
h3 { margin: 0.25rem 0; }
h3 a { color: #1a0dab; text-decoration: none; font-size: 1.1rem; }
h3 a:hover { text-decoration: underline; }
.url { font-size: 0.8rem; color: #006621; margin-bottom: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.snippet { font-size: 0.95rem; color: #444; line-height: 1.5; }
</style>
