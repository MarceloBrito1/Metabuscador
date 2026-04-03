<script setup>
defineProps({
  result: {
    type: Object,
    required: true,
  },
})

function sourceClass(source) {
  if (!source) return ''
  const s = source.toLowerCase()
  if (s.includes('duck')) return 'badge--ddg'
  if (s.includes('wiki')) return 'badge--wiki'
  return 'badge--default'
}
</script>

<template>
  <article class="result-card">
    <div class="result-card__header">
      <a
        class="result-card__title"
        :href="result.url"
        target="_blank"
        rel="noopener noreferrer"
      >
        {{ result.title }}
      </a>
      <span class="badge" :class="sourceClass(result.source)">{{ result.source }}</span>
    </div>
    <p class="result-card__url">{{ result.url }}</p>
    <p class="result-card__snippet">{{ result.snippet }}</p>
  </article>
</template>

<style scoped>
.result-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow);
  transition: box-shadow 0.15s;
}

.result-card:hover {
  box-shadow: var(--shadow-lg);
}

.result-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.result-card__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
  flex: 1;
  line-height: 1.4;
}

.result-card__url {
  font-size: 0.78rem;
  color: #16a34a;
  margin-bottom: 0.4rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-card__snippet {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

.badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge--ddg {
  background: #fff1ee;
  color: var(--color-ddg);
  border: 1px solid #fdd5cc;
}

.badge--wiki {
  background: #eef2ff;
  color: var(--color-wiki);
  border: 1px solid #c7d2fe;
}

.badge--default {
  background: #f1f5f9;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}
</style>
