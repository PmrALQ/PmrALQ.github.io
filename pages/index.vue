<template>
  <div>
    <!-- Hero Section — Two Column -->
    <section class="relative overflow-hidden px-6 py-24 sm:py-32 lg:py-40">
      <div class="mx-auto max-w-5xl">
        <div class="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
          <!-- Left: Text -->
          <div class="relative z-10">
            <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl lg:text-6xl leading-tight">
              {{ t('home.hero.greeting') }}
              <br />
              <span class="bg-gradient-to-r from-primary-500 via-primary-600 to-cyan-500 bg-clip-text text-transparent">
                {{ name }}
              </span>
            </h1>
            <p class="mt-4 text-xl text-gray-500 dark:text-gray-400 sm:text-2xl">
              {{ t('home.hero.role') }}
            </p>
            <p class="mt-4 text-lg text-gray-400 dark:text-gray-500 leading-relaxed max-w-md">
              {{ t('home.hero.description') }}
            </p>
            <div class="mt-8">
              <SocialLinks />
            </div>
          </div>

          <!-- Right: Rich water-blue decorative design -->
          <div class="relative hidden lg:flex items-center justify-center">
            <div class="relative w-[380px] h-[380px]">
              <div class="absolute inset-0 rounded-full border-[6px] border-primary-100 dark:border-primary-900/40 animate-spin-slow opacity-70" />
              <div class="absolute inset-3 rounded-full border-[4px] border-dashed border-primary-200 dark:border-primary-800/50 animate-spin-slower opacity-60" />
              <div class="absolute inset-8 rounded-full border-[5px] border-primary-300 dark:border-primary-700 animate-spin-medium opacity-50" />
              <div class="absolute inset-16 rounded-full bg-gradient-to-br from-primary-200 via-primary-100 to-cyan-100 dark:from-primary-900/50 dark:via-primary-800/40 dark:to-cyan-900/30 flex items-center justify-center shadow-2xl shadow-primary-200/60 dark:shadow-primary-900/40">
                <div class="text-center">
                  <svg class="w-28 h-28 mx-auto" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polygon points="60,10 108,35 108,85 60,110 12,85 12,35" stroke="currentColor" stroke-width="1.5" opacity="0.2" class="text-primary-400 dark:text-primary-500" />
                    <polygon points="60,25 95,43 95,77 60,95 25,77 25,43" stroke="currentColor" stroke-width="2" opacity="0.5" class="text-primary-500 dark:text-primary-400" />
                    <text x="60" y="55" text-anchor="middle" font-size="14" font-family="monospace" font-weight="bold" opacity="0.6" fill="currentColor" class="text-primary-600 dark:text-primary-400">&lt;/&gt;</text>
                    <circle cx="60" cy="70" r="4" fill="currentColor" class="text-primary-500 dark:text-primary-400" />
                    <line x1="60" y1="55" x2="60" y2="66" stroke="currentColor" stroke-width="2" opacity="0.5" class="text-primary-400 dark:text-primary-500" />
                    <circle cx="60" cy="10" r="3" fill="currentColor" class="text-primary-400 dark:text-primary-500" opacity="0.7" />
                    <circle cx="108" cy="35" r="2.5" fill="currentColor" class="text-primary-300 dark:text-primary-600" opacity="0.6" />
                    <circle cx="108" cy="85" r="2" fill="currentColor" class="text-primary-400 dark:text-primary-500" opacity="0.5" />
                    <circle cx="60" cy="110" r="3" fill="currentColor" class="text-primary-300 dark:text-primary-600" opacity="0.7" />
                    <circle cx="12" cy="85" r="2.5" fill="currentColor" class="text-primary-400 dark:text-primary-500" opacity="0.6" />
                    <circle cx="12" cy="35" r="2" fill="currentColor" class="text-primary-300 dark:text-primary-600" opacity="0.5" />
                  </svg>
                  <span class="block mt-4 text-xs font-mono font-bold text-primary-500 dark:text-primary-400 tracking-[0.3em] uppercase">PmrALQ</span>
                </div>
              </div>
              <div
                v-for="dot in floatingDots"
                :key="dot.id"
                class="absolute rounded-full animate-float"
                :style="{
                  width: dot.size + 'px',
                  height: dot.size + 'px',
                  left: dot.x + '%',
                  top: dot.y + '%',
                  backgroundColor: dot.color,
                  opacity: dot.opacity,
                  animationDelay: dot.delay + 's',
                  animationDuration: dot.duration + 's',
                  boxShadow: `0 0 ${dot.size * 3}px ${dot.color}40`,
                }"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="absolute inset-0 -z-10 overflow-hidden">
        <div class="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] rounded-full bg-gradient-to-br from-primary-100/50 via-primary-50/20 to-transparent dark:from-primary-900/30 dark:via-primary-800/10 dark:to-transparent" />
        <div class="absolute right-0 bottom-0 translate-x-1/4 translate-y-1/4 w-[500px] h-[500px] rounded-full bg-gradient-to-tl from-cyan-100/30 to-transparent dark:from-cyan-900/15 dark:to-transparent" />
        <div class="absolute left-0 bottom-0 -translate-x-1/4 translate-y-1/4 w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-primary-100/30 to-transparent dark:from-primary-900/10 dark:to-transparent" />
      </div>
    </section>

    <!-- Wave divider -->
    <div class="relative h-16 -mt-8 overflow-hidden">
      <svg class="absolute bottom-0 w-full h-16 text-white dark:text-gray-950" viewBox="0 0 1440 64" preserveAspectRatio="none" fill="currentColor">
        <path d="M0,32 C180,48 360,16 540,32 C720,48 900,16 1080,32 C1260,48 1440,32 1440,32 L1440,64 L0,64 Z" opacity="0.5" />
        <path d="M0,48 C240,28 480,64 720,48 C960,32 1200,56 1440,48 L1440,64 L0,64 Z" />
      </svg>
    </div>

    <!-- Featured Works -->
    <section class="px-6 pb-24 pt-8">
      <div class="mx-auto max-w-5xl">
        <div class="flex items-center justify-between mb-10">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white sm:text-3xl">
            {{ t('home.latestWorks') }}
          </h2>
          <NuxtLink
            :to="localePath('/archive')"
            class="group inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
          >
            {{ t('blog.allPosts') }}
            <span class="group-hover:translate-x-1 transition-transform">→</span>
          </NuxtLink>
        </div>

        <div v-if="works && works.length > 0" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <template v-for="item in works" :key="item.stem">
            <BlogCard v-if="!item.demoUrl && !item.tech" :post="item" />
            <ProjectCard v-else :project="item" />
          </template>
        </div>
        <div v-else class="text-center py-16">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-900/20 mb-4">
            <svg class="w-8 h-8 text-primary-300 dark:text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-gray-400 dark:text-gray-500">{{ t('home.noWorks') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const localePath = useLocalePath()

const name = 'PmrALQ'

const floatingDots = [
  { id: 1, x: 8, y: 10, size: 8, color: '#38bdf8', opacity: 0.6, delay: 0, duration: 4 },
  { id: 2, x: 85, y: 18, size: 5, color: '#7dd3fc', opacity: 0.5, delay: 0.7, duration: 3.5 },
  { id: 3, x: 15, y: 80, size: 6, color: '#0ea5e9', opacity: 0.4, delay: 1.4, duration: 5 },
  { id: 4, x: 78, y: 75, size: 10, color: '#bae6fd', opacity: 0.5, delay: 0.3, duration: 4.5 },
  { id: 5, x: 90, y: 55, size: 4, color: '#38bdf8', opacity: 0.55, delay: 2.1, duration: 3 },
  { id: 6, x: 5, y: 45, size: 7, color: '#7dd3fc', opacity: 0.4, delay: 1.0, duration: 6 },
  { id: 7, x: 50, y: 5, size: 5, color: '#0ea5e9', opacity: 0.45, delay: 1.8, duration: 3.8 },
  { id: 8, x: 45, y: 92, size: 6, color: '#bae6fd', opacity: 0.5, delay: 2.5, duration: 4.2 },
]

const { data: works } = await useAsyncData('home-works', async () => {
  const posts = await queryCollection('content')
    .where('path', 'LIKE', `/${locale.value}/blog/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()

  const projects = await queryCollection('projects')
    .where('path', 'LIKE', '/projects/%')
    .order('date', 'DESC')
    .limit(3)
    .all()

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
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes spin-slower { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
@keyframes spin-medium { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
@keyframes float { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-12px) scale(1.15); } }
.animate-spin-slow { animation: spin-slow 25s linear infinite; }
.animate-spin-slower { animation: spin-slower 18s linear infinite; }
.animate-spin-medium { animation: spin-medium 15s linear infinite; }
.animate-float { animation: float 4s ease-in-out infinite; }
</style>
