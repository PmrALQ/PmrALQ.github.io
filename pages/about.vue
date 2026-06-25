<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <!-- Page Hero -->
      <PageHero :title="t('about.title')" :description="t('about.description')" />

      <!-- Content from markdown -->
      <article class="prose prose-gray dark:prose-invert max-w-none mt-12">
        <ContentRenderer v-if="page" :value="page" />
        <p v-else class="text-gray-500 dark:text-gray-400">
          {{ t('home.noPosts') }}
        </p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()

const { data: page } = await useAsyncData(
  `about-${locale.value}`,
  async () => {
    const result = await queryCollection('content')
      .where('path', '=', `/${locale.value}/about`)
      .limit(1)
      .all()
    return result[0] || null
  },
  { watch: [locale] }
)

useHead({
  title: t('about.title'),
  meta: [
    { name: 'description', content: t('about.description') },
  ],
})
</script>
