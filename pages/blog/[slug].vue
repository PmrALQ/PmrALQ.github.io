<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <!-- Back links -->
      <div class="flex items-center gap-6 mb-8">
        <NuxtLink
          :to="localePath('/')"
          class="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
        >
          ← {{ t('nav.home') }}
        </NuxtLink>
        <NuxtLink
          :to="localePath('/archive')"
          class="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
        >
          ← {{ t('nav.archive') }}
        </NuxtLink>
      </div>

      <article class="prose prose-gray dark:prose-invert max-w-none">
        <header class="mb-10">
          <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl !mb-4">
            {{ page?.title }}
          </h1>
          <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <time v-if="page?.date" :datetime="page.date">
              {{ formatDate(page.date) }}
            </time>
            <span v-if="page?.tags?.length" class="flex gap-2">
              <span
                v-for="tag in page.tags"
                :key="tag"
                class="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300"
              >
                #{{ tag }}
              </span>
            </span>
          </div>
        </header>

        <ContentRenderer v-if="page" :value="page" />
        <p v-else class="text-gray-500 dark:text-gray-400">
          {{ t('home.noWorks') }}
        </p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()

const slug = computed(() => route.params.slug as string)

// Watch both slug and locale — re-fetch when language switches
const { data: page } = await useAsyncData(
  `blog-${slug.value}-${locale.value}`,
  async () => {
    const result = await queryCollection('content')
      .where('path', '=', `/${locale.value}/blog/${slug.value}`)
      .limit(1)
      .all()
    return result[0] || null
  },
  { watch: [slug, locale] }
)

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

useHead({
  title: computed(() => page.value?.title || t('blog.title')),
  meta: [
    { name: 'description', content: computed(() => page.value?.description || t('blog.description')) },
  ],
})
</script>
