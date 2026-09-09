<template>
  <div class="panel-unified">
    <div class="panel-row">
      <div class="flex items-center gap-3 flex-wrap mb-3">
        <span class="tag-accent">{{ entry.version }}</span>
        <time class="tabular-nums text-sm" style="color:var(--text-3);">
          {{ formatDate(entry.date) }}
        </time>
      </div>
      <h3 style="font-size:17px; font-weight:600; letter-spacing:-0.01em; line-height:1.45; color:var(--text);">
        {{ entry.title }}
      </h3>
      <p v-if="entry.description" class="mt-2 text-sm" style="color:var(--text-2); line-height:1.6;">
        {{ entry.description }}
      </p>
      <div v-if="entry.body" class="mt-4 prose max-w-none text-sm" style="color:var(--text-body); line-height:1.85;">
        <ContentRenderer :value="entry.body" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()

defineProps<{
  entry: {
    title: string
    description?: string
    date: string
    version: string
    body?: unknown
  }
}>()

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>
