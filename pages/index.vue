<template>
  <div>
    <!-- Hero Section — Two Column -->
    <section class="relative overflow-hidden px-6 py-24 sm:py-32 lg:py-40">
      <div class="mx-auto max-w-5xl">
        <div class="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <!-- Left: Text -->
          <div>
            <p class="text-sm font-medium text-primary-600 dark:text-primary-400 mb-4 tracking-wide uppercase">
              {{ t('nav.home') }}
            </p>
            <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl lg:text-6xl leading-tight">
              {{ t('home.hero.greeting') }} <span class="text-primary-600 dark:text-primary-400">{{ name }}</span>
            </h1>
            <p class="mt-4 text-xl text-gray-500 dark:text-gray-400 sm:text-2xl">
              {{ t('home.hero.role') }}
            </p>
            <p class="mt-4 text-lg text-gray-500 dark:text-gray-400 leading-relaxed">
              {{ t('home.hero.description') }}
            </p>
            <div class="mt-8">
              <SocialLinks />
            </div>
          </div>

          <!-- Right: Water-blue decorative design -->
          <div class="relative hidden lg:block">
            <div class="relative w-full aspect-square max-w-[400px] mx-auto">
              <!-- Outer ring -->
              <div class="absolute inset-0 rounded-full border-4 border-primary-200 dark:border-primary-800 animate-[spin_20s_linear_infinite] opacity-60" />
              <!-- Middle ring (offset, opposite spin) -->
              <div class="absolute inset-4 rounded-full border-[3px] border-dashed border-primary-300 dark:border-primary-700 animate-[spin_15s_linear_infinite_reverse] opacity-50" />
              <!-- Inner geometric shape -->
              <div class="absolute inset-12 rounded-3xl bg-gradient-to-br from-primary-200 via-primary-100 to-transparent dark:from-primary-900/40 dark:via-primary-800/30 dark:to-transparent flex items-center justify-center shadow-lg shadow-primary-200/50 dark:shadow-primary-900/30">
                <div class="text-center">
                  <!-- Abstract water-blue symbol -->
                  <svg class="w-24 h-24 mx-auto text-primary-400 dark:text-primary-500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Concentric circles -->
                    <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="2" opacity="0.3" />
                    <circle cx="50" cy="50" r="35" stroke="currentColor" stroke-width="2" opacity="0.5" />
                    <circle cx="50" cy="50" r="22" stroke="currentColor" stroke-width="2.5" opacity="0.8" />
                    <!-- Dot in center -->
                    <circle cx="50" cy="50" r="5" fill="currentColor" />
                    <!-- Wave dots -->
                    <circle cx="20" cy="35" r="4" fill="currentColor" opacity="0.4" />
                    <circle cx="75" cy="30" r="3" fill="currentColor" opacity="0.5" />
                    <circle cx="80" cy="65" r="3.5" fill="currentColor" opacity="0.45" />
                    <circle cx="25" cy="70" r="3" fill="currentColor" opacity="0.35" />
                  </svg>
                  <span class="block mt-3 text-sm font-medium text-primary-500 dark:text-primary-400 tracking-widest uppercase">
                    PmrALQ
                  </span>
                </div>
              </div>
              <!-- Floating dots -->
              <div class="absolute top-4 right-8 w-3 h-3 rounded-full bg-primary-400 dark:bg-primary-500 animate-pulse shadow-lg shadow-primary-300/50" />
              <div class="absolute bottom-10 left-6 w-2.5 h-2.5 rounded-full bg-primary-300 dark:bg-primary-600 animate-pulse shadow-lg shadow-primary-300/50" style="animation-delay: 0.8s" />
              <div class="absolute top-12 left-4 w-2 h-2 rounded-full bg-primary-500 dark:bg-primary-400 animate-pulse shadow-lg shadow-primary-400/50" style="animation-delay: 1.6s" />
            </div>
          </div>
        </div>
      </div>

      <!-- Background decoration -->
      <div class="absolute inset-0 -z-10 overflow-hidden">
        <div class="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-primary-100/40 to-transparent dark:from-primary-900/20" />
      </div>
    </section>

    <!-- Featured Works -->
    <section class="px-6 pb-24">
      <div class="mx-auto max-w-5xl">
        <div class="flex items-center justify-between mb-10">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white sm:text-3xl">
            {{ t('home.latestWorks') }}
          </h2>
          <NuxtLink
            :to="localePath('/archive')"
            class="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
          >
            {{ t('blog.allPosts') }} →
          </NuxtLink>
        </div>

        <!-- Mixed grid: blog posts + projects -->
        <div v-if="works && works.length > 0" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <template v-for="item in works" :key="item._path || item.stem">
            <!-- Blog post card -->
            <BlogCard v-if="item._path && !item.demoUrl && !item.tech" :post="item" />
            <!-- Project card -->
            <ProjectCard v-else :project="item" />
          </template>
        </div>
        <p v-else class="text-center text-gray-500 dark:text-gray-400 py-12">
          {{ t('home.noWorks') }}
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()

const name = 'PmrALQ'

// Fetch both blog posts and projects, merge and sort by date
const { data: works } = await useAsyncData('home-works', async () => {
  const posts = await queryCollection('content')
    .where('path', 'LIKE', `/${locale.value}/blog/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()

  const projects = await queryCollection('projects')
    .where('path', 'LIKE', `/${locale.value}/projects/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()

  // Merge and sort by date, take top 6
  const all = [...posts, ...projects]
    .filter(item => item.date)
    .sort((a, b) => new Date(b.date!).getTime() - new Date(a.date!).getTime())
    .slice(0, 6)

  return all
}, { watch: [locale] })

useHead({
  title: t('siteName'),
  meta: [
    { name: 'description', content: t('home.hero.description') },
  ],
})
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes spin_reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}
</style>
