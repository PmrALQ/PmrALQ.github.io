<template>
  <NuxtLink
    :to="localePath(`/blog/${slug}`)"
    class="card-apple block text-decoration-none"
    style="color:var(--text); text-decoration:none;"
  >
    <!-- 封面：博客无缩略图，用主题渐变补齐 16:9，使卡片结构与项目卡一致（v2 · 2026-09-19） -->
    <div class="aspect-video blog-cover">
      <span class="blog-cover-chip">{{ coverLabel }}</span>
    </div>

    <div class="p-[18px] card-body">
      <div class="flex items-center gap-3 text-sm mb-3" style="color:var(--text-2);">
        <time v-if="post.date" :datetime="post.date" class="tabular-nums">
          {{ formatDate(post.date) }}
        </time>
        <span v-if="post.tags?.length" class="flex gap-1.5">
          <span
            v-for="tag in post.tags?.slice(0, 2)"
            :key="tag"
            class="tag-plain"
          >
            {{ tag }}
          </span>
        </span>
      </div>

      <h3 style="font-size:17px; font-weight:600; letter-spacing:-0.01em; line-height:1.45; color:var(--text); margin-bottom:6px;">
        {{ post.title }}
      </h3>

      <p v-if="post.description" class="line-clamp-2" style="font-size:13.5px; color:var(--text-2); line-height:1.5;">
        {{ post.description }}
      </p>
    </div>
  </NuxtLink>
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

const slug = computed(() => {
  const stem = props.post.stem || ''
  const parts = stem.split('/')
  return parts[parts.length - 1]
})

// 封面标签：优先用文章第一个标签，退回「文章 / Post」
const coverLabel = computed(() => {
  const t = props.post.tags?.[0]
  if (t) return t
  return locale.value === 'zh' ? '文章' : 'Post'
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
