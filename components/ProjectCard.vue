<template>
  <NuxtLink
    :to="localePath(link)"
    class="card-apple group overflow-hidden block text-decoration-none"
    style="color:var(--text); text-decoration:none;"
  >
    <!-- Thumbnail -->
    <div v-if="project.thumbnail" class="aspect-video overflow-hidden" style="background:var(--hover);">
      <img
        :src="project.thumbnail"
        :alt="project.title"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
      />
    </div>
    <div v-else class="aspect-video flex items-center justify-center" style="background:var(--hover);">
      <span class="text-4xl">{{ project.type === 'game' ? '🎮' : '💻' }}</span>
    </div>

    <div class="p-[18px] card-body">
      <div class="flex items-center gap-2 mb-3">
        <span v-if="project.type" class="tag-accent">
          {{ project.type }}
        </span>
        <time v-if="project.date" class="tabular-nums" style="font-size:12px; color:var(--text-3);">
          {{ formatDate(project.date) }}
        </time>
      </div>

      <h3 style="font-size:17px; font-weight:600; letter-spacing:-0.01em; line-height:1.45; color:var(--text); margin-bottom:6px;">
        {{ project.title }}
      </h3>

      <p v-if="project.description" class="line-clamp-2 mb-3" style="font-size:13.5px; color:var(--text-2); line-height:1.5;">
        {{ project.description }}
      </p>

      <!-- 标签限量：最多 4 个，其余折叠为 +N
           （v2 · 2026-09-19 标签过多会把卡片撑得比同排卡片高，导致高度参差） -->
      <div v-if="visibleTech.length" class="flex flex-wrap gap-1.5">
        <span
          v-for="t in visibleTech"
          :key="t"
          class="tag-plain"
        >
          {{ t }}
        </span>
        <span v-if="restTechCount > 0" class="tag-plain">+{{ restTechCount }}</span>
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
// const { locale } = useI18n() // 原仅服务于已抽离的 formatDate
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

// 标签最多显示 4 个，其余折叠为 +N，避免卡片高度被标签行数带偏
const MAX_TECH = 4
const visibleTech = computed(() => (props.project.tech || []).slice(0, MAX_TECH))
const restTechCount = computed(() => Math.max(0, (props.project.tech?.length || 0) - MAX_TECH))

const link = computed(() => {
  const stem = props.project.stem || ''
  const parts = stem.split('/')
  const slug = parts[parts.length - 1]
  return `/projects/${slug}`
})

/*
 * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），
 * 此处保留原始实现供回溯。
 * function formatDate(dateStr: string): string {
 * const date = new Date(dateStr)
 * if (isNaN(date.getTime())) return dateStr
 * return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
 * year: 'numeric',
 * month: 'short',
 * day: 'numeric',
 * })
 * }
 */
</script>
