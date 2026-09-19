<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-read);">
    <NuxtLink
      :to="localePath('/')"
      data-animate
      class="inline-flex items-center text-sm font-medium transition-colors mb-8"
      style="color:var(--accent); text-decoration:none;"
    >
      {{ t('projects.backToProjects') }}
    </NuxtLink>

    <header data-animate data-animate-delay="0.08" class="mb-10">
      <div class="flex items-center gap-3 mb-4 flex-wrap">
        <span v-if="page?.type" class="tag-accent">
          {{ page.type }}
        </span>
        <time v-if="page?.date" class="tabular-nums text-sm" style="color:var(--text-3);">{{ formatDate(page.date) }}</time>
      </div>
      <h1 style="font-size:clamp(27px,5vw,46px); font-weight:700; letter-spacing:-0.03em; line-height:1.1; color:var(--text);">
        {{ page?.title }}
      </h1>
      <p v-if="page?.description" class="mt-4" style="font-size:clamp(15px,2.5vw,18px); color:var(--text-2); line-height:1.6;">
        {{ page.description }}
      </p>
    </header>

    <!-- Demo iframe -->
    <div v-if="page?.demoUrl" class="mb-12 rounded-panel overflow-hidden" style="border:1px solid var(--hairline); box-shadow:var(--sh-panel);">
      <div class="flex items-center justify-between px-5 py-3" style="background:var(--hover); border-bottom:1px solid var(--hairline);">
        <div class="flex items-center gap-2">
          <div class="flex gap-1.5">
            <span class="inline-block rounded-full" style="width:12px; height:12px; background:#ed6a5e;" />
            <span class="inline-block rounded-full" style="width:12px; height:12px; background:#f4bf4f;" />
            <span class="inline-block rounded-full" style="width:12px; height:12px; background:#61c454;" />
          </div>
          <span class="text-xs font-medium ml-3" style="color:var(--text-3);">{{ t('projects.viewDemo') }}</span>
        </div>
        <a :href="page.demoUrl" target="_blank" class="text-xs font-medium transition-colors" style="color:var(--accent); text-decoration:none;">
          {{ t('projects.openFullscreen') }}
        </a>
      </div>
      <div class="aspect-video">
        <iframe :src="page.demoUrl" class="w-full h-full border-0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope" allowfullscreen title="Project demo" />
      </div>
    </div>

    <!-- Tech stack -->
    <div v-if="page?.tech?.length" class="mb-8">
      <h3 class="text-sm font-semibold mb-3 uppercase tracking-wider" style="color:var(--text);">{{ t('projects.techStack') }}</h3>
      <div class="flex flex-wrap gap-2">
        <span v-for="t in page.tech" :key="t" class="tag-accent">
          {{ t }}
        </span>
      </div>
    </div>

    <!-- Source code -->
    <div v-if="page?.sourceUrl" class="mb-10">
      <a :href="page.sourceUrl" target="_blank" rel="noopener noreferrer" class="btn-apple btn-secondary gap-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
        </svg>
        {{ t('projects.sourceCode') }}
      </a>
    </div>

    <!-- Body content -->
    <article data-animate data-animate-delay="0.18" class="prose max-w-none" style="line-height:1.85; color:var(--text-body);">
      <ContentRenderer v-if="page" :value="page" />
    </article>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const pageRoot = ref<HTMLElement>()
usePageAnimations(pageRoot)

const slug = computed(() => route.params.slug as string)

const { data: page } = await useAsyncData(
  `project-${locale.value}-${slug.value}`,
  async () => {
    const result = await queryCollection('projects')
      // 路径带 locale 前缀(如 /zh/projects/sample-game), 与 i18n prefix 策略对齐
      .where('path', '=', `/${locale.value}/projects/${slug.value}`)
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
