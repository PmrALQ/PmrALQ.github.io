<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-read);">
    <!-- Back links -->
    <div class="flex items-center gap-6 mb-8">
      <NuxtLink
        :to="localePath('/')"
        class="inline-flex items-center text-sm font-medium transition-colors"
        style="color:var(--accent); text-decoration:none;"
      >
        ← {{ t('nav.home') }}
      </NuxtLink>
      <NuxtLink
        :to="localePath('/archive')"
        class="inline-flex items-center text-sm font-medium transition-colors"
        style="color:var(--accent); text-decoration:none;"
      >
        ← {{ t('nav.archive') }}
      </NuxtLink>
    </div>

    <article class="prose max-w-none">
      <header data-animate class="mb-10">
        <h1 style="font-size:clamp(27px,5vw,46px); font-weight:700; letter-spacing:-0.03em; line-height:1.1; color:var(--text);">
          {{ page?.title }}
        </h1>
        <div class="flex items-center gap-4 mt-4 text-sm" style="color:var(--text-3);">
          <time v-if="page?.date" :datetime="page.date" class="tabular-nums">
            {{ formatDate(page.date) }}
          </time>
          <span v-if="page?.tags?.length" class="flex gap-2">
            <span
              v-for="tag in page.tags"
              :key="tag"
              class="tag-plain"
            >
              {{ tag }}
            </span>
          </span>
        </div>
      </header>

      <template v-if="page">
        <div data-animate data-animate-delay="0.12">
          <ContentRenderer :value="page" />
        </div>
      </template>
      <p v-else style="color:var(--text-3);">
        {{ t('home.noWorks') }}
      </p>
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
