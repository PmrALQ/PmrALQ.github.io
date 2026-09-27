<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-read);">
    <div data-animate>
      <PageHero :title="t('archive.title')" :description="t('archive.description')" />
    </div>
    <div data-animate data-animate-delay="0.12">
      <CategoryFilter :active="activeCategory" @select="activeCategory = $event" />
    </div>
    <div data-animate data-animate-delay="0.2">
      <ArchiveTimeline :items="filteredPosts" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { categoryTagMap } from '~/utils/tags'

const { t, locale } = useI18n()
const pageRoot = ref<HTMLElement>()
const activeCategory = ref('all')
usePageAnimations(pageRoot)

// 归档收录「文章 + 作品」两类内容，共用同一条时间轴：
// 文章查 content 集合的 blog 目录，作品查 projects 集合（自带 tech/type 等字段）。
// 早先这里只查了 blog 目录，所以新加的 project 不会出现在归档里。
const { data: allItems } = await useAsyncData(
  `archive-items-${locale.value}`,
  async () => {
    const posts = await queryCollection('content')
      .where('path', 'LIKE', `/${locale.value}/blog/%`)
      .all()

    const projects = await queryCollection('projects')
      .where('path', 'LIKE', `/${locale.value}/projects/%`)
      .all()

    return [
      ...posts.map(p => ({ ...p, link: `/blog/${(p.stem || '').split('/').pop()}` })),
      ...projects.map(p => ({ ...p, link: `/projects/${(p.stem || '').split('/').pop()}` })),
    ]
      .filter(item => item.date)
      .sort((a, b) => new Date(b.date!).getTime() - new Date(a.date!).getTime())
  },
  { watch: [locale] }
)

const filteredPosts = computed(() => {
  const items = allItems.value || []
  const matchTags = categoryTagMap[activeCategory.value] || []
  const filtered = activeCategory.value === 'all'
    ? items
    : items.filter(p => p.tags?.some((tag: string) => matchTags.includes(tag)))
  return filtered.map(p => ({
    title: p.title,
    description: p.description,
    date: p.date,
    tags: p.tags,
    link: p.link,
  }))
})

useHead({
  title: t('archive.title'),
  meta: [{ name: 'description', content: t('archive.description') }],
})
</script>
