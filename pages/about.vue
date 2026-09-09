<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-read);">
    <div data-animate>
      <PageHero :title="t('about.title')" :description="t('about.description')" />
    </div>
    <article data-animate data-animate-delay="0.15" class="prose max-w-none mt-12" style="line-height:1.85; color:var(--text-body);">
      <ContentRenderer v-if="page" :value="page" />
      <p v-else style="color:var(--text-3);">
        {{ t('home.noWorks') }}
      </p>
    </article>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const pageRoot = ref<HTMLElement>()
usePageAnimations(pageRoot)

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
  meta: [{ name: 'description', content: t('about.description') }],
})
</script>
