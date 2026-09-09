<template>
  <NuxtLink
    :to="localePath(`/blog/${slug}`)"
    class="card-apple p-[18px] block text-decoration-none"
    style="color:var(--text); text-decoration:none;"
  >
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
