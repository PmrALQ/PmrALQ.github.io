<template>
  <div class="relative">
    <!-- Vertical line -->
    <div class="absolute left-[19px] top-3 bottom-3 w-0.5 bg-gradient-to-b from-primary-300 via-primary-200 to-transparent dark:from-primary-600 dark:via-primary-800" />

    <!-- Timeline items -->
    <div class="space-y-1">
      <div v-for="(item, index) in items" :key="index" class="relative flex items-start gap-5 group">
        <!-- Date node -->
        <div class="relative z-10 flex-shrink-0 mt-5">
          <div class="w-[40px] h-[40px] rounded-full bg-primary-100 dark:bg-primary-900/40 border-2 border-primary-300 dark:border-primary-600 flex items-center justify-center transition-all group-hover:border-primary-500 group-hover:bg-primary-200 dark:group-hover:bg-primary-800/40">
            <div class="w-2.5 h-2.5 rounded-full bg-primary-500 dark:bg-primary-400" />
          </div>
        </div>

        <!-- Content bar -->
        <NuxtLink
          :to="localePath(item.link)"
          class="flex-1 mt-4 p-5 rounded-2xl border border-gray-200 bg-white hover:border-primary-300 hover:shadow-md hover:shadow-primary-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700 dark:hover:shadow-primary-900/5 transition-all duration-300 group/link"
        >
          <div class="flex items-center justify-between gap-4 flex-wrap">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 flex-wrap mb-2">
                <time class="text-xs font-mono text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2.5 py-1 rounded-full">
                  {{ formatDate(item.date) }}
                </time>
                <h3 class="text-base font-semibold text-gray-900 dark:text-white truncate">
                  {{ item.title }}
                </h3>
              </div>
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  v-for="tag in item.tags?.slice(0, 3)"
                  :key="tag"
                  class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                >
                  #{{ tag }}
                </span>
                <p v-if="item.description" class="text-sm text-gray-400 dark:text-gray-500 truncate ml-2">
                  {{ item.description }}
                </p>
              </div>
            </div>
            <span class="text-primary-400 dark:text-primary-500 text-lg font-semibold group-hover/link:translate-x-1 transition-transform shrink-0">→</span>
          </div>
        </NuxtLink>
      </div>
    </div>

    <!-- Empty -->
    <p v-if="items.length === 0" class="text-center text-gray-400 dark:text-gray-500 py-16">
      {{ t('archive.noPosts') }}
    </p>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()

defineProps<{
  items: Array<{
    title: string
    description?: string
    date?: string
    tags?: string[]
    link: string
  }>
}>()

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    month: 'short',
    day: 'numeric',
  })
}
</script>
