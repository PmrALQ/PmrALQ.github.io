<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <PageHero :title="t('guestbook.title')" :description="t('guestbook.description')" />

      <!-- Content from markdown -->
      <article class="prose prose-gray dark:prose-invert max-w-none mt-12">
        <ContentRenderer v-if="page" :value="page" />
        <p v-else class="text-gray-500 dark:text-gray-400">
          {{ t('home.noWorks') }}
        </p>
      </article>

      <!-- Waline mount point (reserved for future activation) -->
      <div id="waline" class="mt-8" />
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()

const { data: page } = await useAsyncData(
  `guestbook-${locale.value}`,
  async () => {
    const result = await queryCollection('content')
      .where('path', '=', `/${locale.value}/guestbook`)
      .limit(1)
      .all()
    return result[0] || null
  },
  { watch: [locale] }
)

useHead({
  title: t('guestbook.title'),
  meta: [{ name: 'description', content: t('guestbook.description') }],
})
</script>
