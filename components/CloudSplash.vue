<template>
  <!-- 开屏加载：水蓝云朵屏，仅首次进站显示（sessionStorage 标记） -->
  <div v-if="show" ref="root" class="splash-overlay">
    <div class="splash-cloud splash-cloud-1"><CloudSprite /></div>
    <div class="splash-cloud splash-cloud-2"><CloudSprite /></div>
    <div class="splash-cloud splash-cloud-3"><CloudSprite /></div>
    <div class="splash-cloud splash-cloud-4"><CloudSprite /></div>

    <div class="splash-title">
      <div class="splash-logo"><CloudSprite /></div>
      <p class="splash-loading">{{ t('splash.loading') }}</p>
      <p class="splash-progress">{{ progress }}%</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { gsap } from 'gsap'
const { t } = useI18n()
const { markSplashFinished } = useSplash()

const show = ref(false)
const progress = ref(0)
const root = ref<HTMLElement>()
let ctx: gsap.Context | null = null

onMounted(async () => {
  // 仅首访显示：sessionStorage 是 origin 级，与 /zh /en 路由无关
  let seen = false
  try {
    seen = sessionStorage.getItem('splash-seen') === '1'
  }
  catch { /* 隐私模式等场景下忽略 */ }

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  // 已看过 / 用户偏好减弱动效 → 不显示，直接放行 hero
  if (seen || reduce) {
    markSplashFinished()
    return
  }

  show.value = true
  try { sessionStorage.setItem('splash-seen', '1') }
  catch { /* ignore */ }

  // 关键：v-if="show" 的 DOM 要等 nextTick 才渲染，
  // 立即建 gsap.context 会拿到 undefined 的 root.value 而抛错
  await nextTick()

  ctx = gsap.context(() => {
    const rootEl = root.value!
    const clouds = rootEl.querySelectorAll<HTMLElement>('.splash-cloud')

    // 云朵空闲漂浮（散开前 kill 防属性冲突）
    const float = gsap.to(clouds, {
      y: '+=14',
      duration: 2.4,
      yoyo: true,
      repeat: -1,
      ease: 'sine.inOut',
      stagger: { each: 0.5 },
    })

    // 进度计数
    const counter = { v: 0 }

    const tl = gsap.timeline()
    tl.from(rootEl, { autoAlpha: 0, duration: 0.15 })
      .to(counter, {
        v: 100,
        duration: 0.7,
        ease: 'power2.inOut',
        onUpdate: () => { progress.value = Math.round(counter.v) },
      }, 0.15)
      .add(() => float.kill(), '+=0.05')
      .to(clouds, {
        x: (i) => (i % 2 ? 1 : -1) * (90 + i * 36),
        y: -70,
        scale: 1.2,
        autoAlpha: 0,
        duration: 0.35,
        stagger: 0.05,
        ease: 'back.in(1.4)',
      }, '-=0.05')
      .to(rootEl, { autoAlpha: 0, duration: 0.3, ease: 'power2.inOut' }, '+=0.05')
      .add(() => {
        show.value = false
        markSplashFinished()
      })
  }, root.value)
})

onUnmounted(() => {
  ctx?.revert()
})
</script>
