<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <!-- Page Hero -->
      <PageHero :title="t('archive.title')" :description="t('archive.description')" />

      <!-- Category Filter -->
      <CategoryFilter :active="activeCategory" @select="activeCategory = $event" />

      <!-- Filtered Timeline -->
      <ArchiveTimeline :items="filteredPosts" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { categoryTagMap } from '~/utils/tags'

const { t, locale } = useI18n()

const activeCategory = ref('all')

// Fetch all blog posts
const { data: allPosts } = await useAsyncData(
  `blog-posts-${locale.value}`,
  async () => {
    const results = await queryCollection('content')
      .where('path', 'LIKE', `/${locale.value}/blog/%`)
      .order('date', 'DESC')
      .all()
    return results
  },
  { watch: [locale] }
)

// Filter by selected category (supports bilingual tags)
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
  title: t('blog.title'),
  meta: [{ name: 'description', content: t('blog.description') }],
})
</script>
