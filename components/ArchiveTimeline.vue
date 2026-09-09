<template>
  <!-- Unified panel: one surface + hairline dividers — no fragmented cards -->
  <div v-if="items.length > 0" class="panel-unified">
    <NuxtLink
      v-for="(item, index) in items"
      :key="index"
      :to="localePath(item.link)"
      class="panel-row"
    >
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 flex-wrap">
            <time class="tabular-nums text-xs font-semibold rounded-full px-2.5 py-0.5" style="color:var(--accent); background:rgba(0,113,227,0.08);">
              {{ formatDate(item.date) }}
            </time>
            <h3 style="font-size:17px; font-weight:600; letter-spacing:-0.01em; line-height:1.45; color:var(--text);" class="truncate">
              {{ item.title }}
            </h3>
          </div>
          <div class="flex items-center gap-2 flex-wrap mt-2">
            <span
              v-for="tag in item.tags?.slice(0, 3)"
              :key="tag"
              class="tag-plain"
            >
              {{ tag }}
            </span>
            <p v-if="item.description" class="text-sm truncate ml-1" style="color:var(--text-3);">
              {{ item.description }}
            </p>
          </div>
        </div>
        <span class="text-lg font-semibold transition-transform group-hover:translate-x-1 shrink-0" style="color:var(--text-4);">
          →
        </span>
      </div>
    </NuxtLink>
  </div>

  <!-- Empty -->
  <p v-else class="text-center py-16" style="color:var(--text-3);">
    {{ t('archive.noPosts') }}
  </p>
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
