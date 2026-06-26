<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <NuxtLink
        :to="localePath('/')"
        class="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors mb-8"
      >
        {{ t('projects.backToProjects') }}
      </NuxtLink>

      <header class="mb-10">
        <div class="flex items-center gap-3 mb-4 flex-wrap">
          <span v-if="page?.type" class="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-600 dark:bg-primary-900/30 dark:text-primary-400">
            {{ page.type }}
          </span>
          <time v-if="page?.date" class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(page.date) }}</time>
        </div>
        <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl !mb-4">{{ page?.title }}</h1>
        <p v-if="page?.description" class="text-lg text-gray-500 dark:text-gray-400">{{ page.description }}</p>
      </header>

      <div v-if="page?.demoUrl" class="mb-12 rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-lg">
        <div class="flex items-center justify-between px-5 py-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <div class="flex gap-1.5">
              <span class="w-3 h-3 rounded-full bg-red-400" />
              <span class="w-3 h-3 rounded-full bg-yellow-400" />
              <span class="w-3 h-3 rounded-full bg-green-400" />
            </div>
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400 ml-3">{{ t('projects.viewDemo') }}</span>
          </div>
          <a :href="page.demoUrl" target="_blank" class="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors">
            {{ t('projects.openFullscreen') }}
          </a>
        </div>
        <div class="aspect-video bg-white">
          <iframe :src="page.demoUrl" class="w-full h-full border-0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope" allowfullscreen title="Project demo" />
        </div>
      </div>

      <div v-if="page?.tech?.length" class="mb-8">
        <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 uppercase tracking-wider">{{ t('projects.techStack') }}</h3>
        <div class="flex flex-wrap gap-2">
          <span v-for="t in page.tech" :key="t" class="inline-flex items-center rounded-full bg-primary-50 px-3 py-1 text-sm font-medium text-primary-700 dark:bg-primary-900/20 dark:text-primary-300">
            {{ t }}
          </span>
        </div>
      </div>

      <div v-if="page?.sourceUrl" class="mb-10">
        <a :href="page.sourceUrl" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:text-primary-600 hover:border-primary-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:hover:text-primary-400 dark:hover:border-primary-700 transition-all shadow-sm">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
          </svg>
          {{ t('projects.sourceCode') }}
        </a>
      </div>

      <article class="prose prose-gray dark:prose-invert max-w-none">
        <ContentRenderer v-if="page" :value="page" />
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()

const slug = computed(() => route.params.slug as string)

const { data: page } = await useAsyncData(
  `project-${slug.value}`,
  async () => {
    const result = await queryCollection('projects')
      .where('path', '=', `/projects/${slug.value}`)
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
  title: computed(() => page.value?.title || t('projects.title')),
  meta: [{ name: 'description', content: computed(() => page.value?.description || t('projects.description')) }],
})
</script>
