<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden px-6 py-24 sm:py-32 lg:py-40">
      <div class="mx-auto max-w-5xl text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl lg:text-6xl">
          {{ t('home.hero.greeting') }} <span class="text-primary-600 dark:text-primary-400">{{ name }}</span>
        </h1>
        <p class="mt-4 text-xl text-gray-500 dark:text-gray-400 sm:text-2xl">
          {{ t('home.hero.role') }}
        </p>
        <p class="mt-6 max-w-2xl mx-auto text-lg text-gray-500 dark:text-gray-400 leading-relaxed">
          {{ t('home.hero.description') }}
        </p>
        <div class="mt-10">
          <SocialLinks />
        </div>
      </div>

      <!-- Background decoration -->
      <div class="absolute inset-0 -z-10 overflow-hidden">
        <div class="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-primary-100/40 to-transparent dark:from-primary-900/20" />
      </div>
    </section>

    <!-- Latest Posts -->
    <section class="px-6 pb-24">
      <div class="mx-auto max-w-5xl">
        <div class="flex items-center justify-between mb-10">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white sm:text-3xl">
            {{ t('home.hero.latestPosts') }}
          </h2>
          <NuxtLink
            :to="localePath('/blog')"
            class="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
          >
            {{ t('blog.allPosts') }} →
          </NuxtLink>
        </div>

        <BlogList v-if="posts && posts.length > 0" :posts="posts" />
        <p v-else class="text-center text-gray-500 dark:text-gray-400 py-12">
          {{ t('home.noPosts') }}
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()

// You can customize these
const name = 'PmrALQ'

// Fetch latest blog posts using Content v3 queryCollection
const { data: posts } = await useAsyncData('home-posts', async () => {
  const results = await queryCollection('content')
    .where('path', 'LIKE', `/${locale.value}/blog/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()
  return results
}, { watch: [locale] })

// SEO
useHead({
  title: t('siteName'),
  meta: [
    { name: 'description', content: t('home.hero.description') },
  ],
})
</script>
