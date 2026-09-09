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

const { data: allPosts } = await useAsyncData(
  `archive-posts-${locale.value}`,
  async () => {
    return await queryCollection('content')
      .where('path', 'LIKE', `/${locale.value}/blog/%`)
      .order('date', 'DESC')
      .all()
  },
  { watch: [locale] }
)

const filteredPosts = computed(() => {
  const posts = allPosts.value || []
  const matchTags = categoryTagMap[activeCategory.value] || []
  const filtered = activeCategory.value === 'all'
    ? posts
    : posts.filter(p => p.tags?.some((t: string) => matchTags.includes(t)))
  return filtered.map(p => ({
    title: p.title,
    description: p.description,
    date: p.date,
    tags: p.tags,
    link: `/blog/${(p.stem || '').split('/').pop()}`,
  }))
})

useHead({
  title: t('archive.title'),
  meta: [{ name: 'description', content: t('archive.description') }],
})
</script>
