<template>
  <div
    class="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md hover:border-primary-300 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700"
  >
    <!-- Thumbnail -->
    <div v-if="project.thumbnail" class="aspect-video overflow-hidden bg-gray-100 dark:bg-gray-800">
      <img
        :src="project.thumbnail"
        :alt="project.title"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
      />
    </div>
    <!-- Placeholder when no thumbnail -->
    <div v-else class="aspect-video flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-50 dark:from-primary-900/30 dark:to-primary-800/20">
      <span class="text-4xl">{{ project.type === 'game' ? '🎮' : '💻' }}</span>
    </div>

    <!-- Content -->
    <div class="p-5">
      <!-- Type badge -->
      <div class="flex items-center gap-2 mb-3">
        <span
          v-if="project.type"
          class="inline-flex items-center rounded-full bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-600 dark:bg-primary-900/30 dark:text-primary-400"
        >
          {{ project.type }}
        </span>
        <time v-if="project.date" class="text-xs text-gray-400 dark:text-gray-500">
          {{ formatDate(project.date) }}
        </time>
      </div>

      <!-- Title -->
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
        <NuxtLink
          :to="localePath(link)"
          class="after:absolute after:inset-0"
        >
          {{ project.title }}
        </NuxtLink>
      </h3>

      <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
        {{ project.description }}
      </p>

      <!-- Tech stack -->
      <div v-if="project.tech?.length" class="flex flex-wrap gap-1.5">
        <span
          v-for="t in project.tech"
          :key="t"
          class="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400"
        >
          {{ t }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localePath = useLocalePath()

const props = defineProps<{
  project: Record<string, unknown> & {
    title: string
    description?: string
    date?: string
    tags?: string[]
    thumbnail?: string
    demoUrl?: string
    sourceUrl?: string
    tech?: string[]
    type?: string
    stem?: string
  }
}>()

const link = computed(() => {
  const stem = props.project.stem || ''
  const parts = stem.split('/')
  const slug = parts[parts.length - 1]
  return `/projects/${slug}`
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>
