<template>
  <div v-if="posts && posts.length > 0" class="panel-unified">
    <NuxtLink
      v-for="post in posts"
      :key="post._path"
      :to="localePath(`/blog/${getSlug(post._path)}`)"
      class="panel-row"
    >
      <div class="flex items-center gap-3 flex-wrap mb-1">
        <time v-if="post.date" class="tabular-nums text-xs font-semibold rounded-full px-2.5 py-0.5" style="color:var(--accent); background:rgba(0,113,227,0.08);">
          {{ formatDate(post.date) }}
        </time>
        <h3 style="font-size:17px; font-weight:600; letter-spacing:-0.01em; line-height:1.45; color:var(--text);">
          {{ post.title }}
        </h3>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <span
          v-for="tag in post.tags?.slice(0, 3)"
          :key="tag"
          class="tag-plain"
        >
          {{ tag }}
        </span>
        <p v-if="post.description" class="text-sm ml-1" style="color:var(--text-3);">
          {{ post.description }}
        </p>
      </div>
    </NuxtLink>
  </div>
  <p v-else class="text-center py-16" style="color:var(--text-3);">
    {{ t('archive.noPosts') }}
  </p>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()

defineProps<{
  posts: Array<{
    _path: string
    title: string
    description?: string
    date?: string
    tags?: string[]
  }>
}>()

function getSlug(path?: string): string {
  if (!path) return ''
  const parts = path.split('/')
  return parts[parts.length - 1]
}

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
