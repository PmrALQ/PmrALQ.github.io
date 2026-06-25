<template>
  <div
    class="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
  >
    <div class="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mb-3">
      <time v-if="post.date" :datetime="post.date">
        {{ formatDate(post.date) }}
      </time>
      <span v-if="post.tags?.length" class="flex gap-1.5">
        <span
          v-for="tag in post.tags?.slice(0, 2)"
          :key="tag"
          class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-800 dark:text-gray-400"
        >
          {{ tag }}
        </span>
      </span>
    </div>

    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
      <NuxtLink
        :to="localePath(`/blog/${slug}`)"
        class="after:absolute after:inset-0"
      >
        {{ post.title }}
      </NuxtLink>
    </h3>

    <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
      {{ post.description }}
    </p>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localePath = useLocalePath()

const props = defineProps<{
  post: Record<string, unknown> & {
    title: string
    description?: string
    date?: string
    tags?: string[]
    stem?: string
  }
}>()

// Extract slug from stem (e.g. "/zh/blog/hello-world" → "hello-world")
const slug = computed(() => {
  const stem = props.post.stem || ''
  const parts = stem.split('/')
  return parts[parts.length - 1]
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
