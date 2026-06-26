<template>
  <div
    class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:border-primary-300 hover:shadow-md dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700"
  >
    <!-- Version badge -->
    <div class="flex items-center gap-3 mb-4">
      <time class="text-sm font-mono text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-3 py-1 rounded-full">
        {{ formatDate(entry.date) }}
      </time>
      <span class="inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-bold text-gray-700 dark:bg-gray-800 dark:text-gray-300 font-mono">
        {{ entry.version }}
      </span>
    </div>

    <!-- Title -->
    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">
      {{ entry.title }}
    </h3>

    <!-- Description -->
    <p v-if="entry.description" class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
      {{ entry.description }}
    </p>

    <!-- Body content -->
    <div v-if="entry.body" class="mt-4 prose prose-gray dark:prose-invert max-w-none text-sm">
      <ContentRenderer :value="entry.body" />
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
