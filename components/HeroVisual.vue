<template>
  <!-- 首页 hero 右侧动效：粉彩雾层 + 光晕 + 玻璃圆盘 + 多层云朵 + 光点 + 鼠标视差 -->
  <div ref="root" class="hero-visual" aria-hidden="true">
    <!-- 背景雾层（最底，呼吸漂移） -->
    <div class="hero-parallax parallax-mist" data-layer="0.4">
      <div class="mist mist-1"></div>
      <div class="mist mist-2"></div>
    </div>
    <div class="hero-parallax parallax-blob" data-layer="0.5">
      <div class="hero-blob"></div>
    </div>

    <!-- 漂浮光点 -->
    <div class="hero-parallax parallax-dots" data-layer="0.7">
      <span class="dot dot-1"></span>
      <span class="dot dot-2"></span>
      <span class="dot dot-3"></span>
      <span class="dot dot-4"></span>
      <span class="dot dot-5"></span>
    </div>

    <!-- 玻璃圆盘（渐变光环缓转 + 盘内云朵反向） -->
    <div class="hero-parallax parallax-disc" data-layer="1">
      <div class="glass-disc">
        <CloudSprite class="disc-cloud" />
      </div>
    </div>

    <!-- 多层云朵：近景 > 远景 -->
    <div class="hero-parallax parallax-cloud-1" data-layer="1.5">
      <CloudSprite class="hero-cloud hero-cloud-1" />
    </div>
    <div class="hero-parallax parallax-cloud-2" data-layer="1">
      <CloudSprite class="hero-cloud hero-cloud-2" />
    </div>
    <div class="hero-parallax parallax-cloud-3" data-layer="0.5">
      <CloudSprite class="hero-cloud hero-cloud-3" />
    </div>
    <div class="hero-parallax parallax-cloud-4" data-layer="2">
      <CloudSprite class="hero-cloud hero-cloud-4" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { gsap } from 'gsap'
const root = ref<HTMLElement>()
let ctx: gsap.Context | null = null
let onMove: ((e: MouseEvent) => void) | null = null

onMounted(() => {
  if (!root.value) return

  ctx = gsap.context(() => {
    const clouds = root.value!.querySelectorAll<HTMLElement>('.hero-cloud, .glass-disc')

    // 云朵 / 圆盘漂浮（不同速度，制造层次）
    gsap.to(clouds, {
      y: '+=22',
      duration: 3.6,
      yoyo: true,
      repeat: -1,
      ease: 'sine.inOut',
      stagger: { each: 0.6 },
    })

    // 圆盘缓转 + 盘内云朵反向旋转
    gsap.to('.glass-disc', { rotation: 360, duration: 60, repeat: -1, ease: 'none' })
    gsap.to('.disc-cloud', { rotation: -360, duration: 60, repeat: -1, ease: 'none' })
  }, root.value)

  // 鼠标视差：仅精细指针 + 非 reduced-motion
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!fine || reduce) return

  const layers = Array.from(root.value.querySelectorAll<HTMLElement>('.hero-parallax'))
  const quick = layers.map((el) => ({
    x: gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3.out' }),
    y: gsap.quickTo(el, 'y', { duration: 0.6, ease: 'power3.out' }),
    depth: parseFloat(el.dataset.layer || '1'),
  }))

  onMove = (e: MouseEvent) => {
    const nx = e.clientX / window.innerWidth - 0.5
    const ny = e.clientY / window.innerHeight - 0.5
    for (const t of quick) {
      t.x(nx * 14 * t.depth)
      t.y(ny * 14 * t.depth)
    }
  }
  window.addEventListener('mousemove', onMove)
})

onUnmounted(() => {
  if (onMove) window.removeEventListener('mousemove', onMove)
  ctx?.revert()
})
</script>
