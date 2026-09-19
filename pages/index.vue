<template>
  <div>
    <!-- Hero：全屏，左文右动效 -->
    <section ref="pageRoot" class="hero-section">
      <div class="hero-inner">
        <div class="hero-left">
          <div class="hero-item text-xs font-semibold tracking-[0.14em] uppercase" style="color:var(--text-3);">
            {{ t('home.hero.role') }}
          </div>
          <h1 class="hero-item" style="margin-top:15px; font-size:clamp(32px,6vw,52px); font-weight:700; letter-spacing:-0.03em; line-height:1.06; color:var(--text);">
            {{ t('home.hero.greeting') }}
            <span style="color:var(--accent);">{{ name }}</span>
          </h1>
          <p class="hero-item" style="margin-top:16px; font-size:clamp(15px,2.5vw,18px); color:var(--text-2); line-height:1.6; max-width:560px; margin-inline:auto;">
            {{ t('home.hero.description') }}
          </p>
          <div class="hero-item mt-8">
            <SocialLinks />
          </div>
        </div>
        <HeroVisual />
      </div>
    </section>

    <!-- Featured Works -->
    <section class="mx-auto px-[22px] section-gap" style="max-width:var(--max-grid)">
      <div data-animate class="flex items-center justify-between mb-10">
        <h2 style="font-size:clamp(20px,3.4vw,26px); font-weight:700; letter-spacing:-0.02em; line-height:1.25; color:var(--text);">
          {{ t('home.latestWorks') }}
        </h2>
        <NuxtLink
          :to="localePath('/archive')"
          class="group inline-flex items-center gap-2 text-sm font-medium transition-colors"
          style="color:var(--accent); text-decoration:none;"
        >
          {{ t('blog.allPosts') }}
          <span class="group-hover:translate-x-1 transition-transform">→</span>
        </NuxtLink>
      </div>

      <!-- Card grid for works -->
      <div v-if="works && works.length > 0" class="grid gap-[14px]" style="grid-template-columns:repeat(auto-fill, minmax(290px, 1fr));">
        <div v-for="item in works" :key="item.stem" class="card-wrap" data-reveal-card data-tilt>
          <span class="tilt-sheen" aria-hidden="true"></span>
          <BlogCard v-if="item._type === 'post'" :post="item" />
          <ProjectCard v-else :project="item" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="text-center py-16">
        <p style="color:var(--text-3);">{{ t('home.noWorks') }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { gsap } from 'gsap'
const { t, locale } = useI18n()
const localePath = useLocalePath()

const name = 'PmrALQ'
const pageRoot = ref<HTMLElement>()

const { splashFinished } = useSplash()

let heroCtx: gsap.Context | null = null
let heroTl: gsap.core.Timeline | null = null

onMounted(() => {
  if (!pageRoot.value) return

  heroCtx = gsap.context(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    // hero 入场：开屏完成后播放（from 的 immediateRender 让元素在开屏期间保持隐藏）
    if (!reduce) {
      heroTl = gsap.timeline({ paused: true })
      heroTl.from(pageRoot.value!.querySelectorAll('.hero-item'), {
        y: 28,
        autoAlpha: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: 'power3.out',
      })
    }

    // hero 滚动淡出（与右侧动效形成景深）
    // 注意：trigger 必须用元素引用——字符串会被 gsap.context scoping
    // 到 pageRoot 内部查找，而 .hero-section 是根元素自身，查不到
    const fadeCfg = {
      trigger: pageRoot.value!,
      start: 'top top',
      end: 'bottom 25%',
      scrub: true,
    }
    gsap.to('.hero-inner', {
      opacity: 0,
      yPercent: -12,
      ease: 'none',
      scrollTrigger: fadeCfg,
    })
    gsap.to('.hero-visual', {
      yPercent: 14,
      ease: 'none',
      scrollTrigger: fadeCfg,
    })
  }, pageRoot.value)

  // 注册顺序：先建 timeline 再 watch，immediate 检查当前 splash 状态
  watch(splashFinished, (done) => {
    if (done) heroTl?.play()
  }, { immediate: true })
})

onUnmounted(() => {
  heroCtx?.revert()
})

// 卡片夸张入场 / 3D tilt / 常规 fade-up
useRevealCards(pageRoot)
useTiltCards(pageRoot)
usePageAnimations(pageRoot)

const { data: works } = await useAsyncData('home-works', async () => {
  const posts = await queryCollection('content')
    .where('path', 'LIKE', `/${locale.value}/blog/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()

  const projects = await queryCollection('projects')
    // 路径带 locale 前缀, 与 i18n prefix 策略对齐
    .where('path', 'LIKE', `/${locale.value}/projects/%`)
    .order('date', 'DESC')
    .limit(3)
    .all()

  const all = [
    ...posts.map(p => ({ ...p, _type: 'post' as const })),
    ...projects.map(p => ({ ...p, _type: 'project' as const })),
  ]
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
