<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-5xl">
      <!-- Page Hero -->
      <PageHero :title="t('blog.title')" :description="t('blog.description')" />

      <!-- Blog List -->
      <BlogList v-if="posts && posts.length > 0" :posts="posts" />
      <p v-else class="text-center text-gray-500 dark:text-gray-400 py-12">
        {{ t('home.noPosts') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()

const { data: posts } = await useAsyncData(
  `blog-list-${locale.value}`,
  async () => {
    const results = await queryCollection('content')
      .where('path', 'LIKE', `/${locale.value}/blog/%`)
      .order('date', 'DESC')
      .all()
    return results
  },
  { watch: [locale] }
)

useHead({
  title: t('blog.title'),
  meta: [
    { name: 'description', content: t('blog.description') },
  ],
})
</script>
