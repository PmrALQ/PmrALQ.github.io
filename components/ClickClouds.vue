<template>
  <!-- 全站点击猫爪：fixed canvas，点击处出现水蓝色猫爪（真实图片 + 柔和雾圈） -->
  <canvas ref="canvas" class="click-clouds" aria-hidden="true"></canvas>
</template>

<script setup lang="ts">
interface Paw {
  x: number
  y: number
  size: number      // 爪印基准尺寸（px）
  angle: number     // 随机旋转
  age: number       // 已存活秒数
  life: number      // 总寿命
}

const canvas = ref<HTMLCanvasElement>()
let ctx2d: CanvasRenderingContext2D | null = null
let raf = 0
let running = false
let last = 0
let reduce = false
let visible = true
let pawImg: HTMLImageElement | null = null
const paws: Paw[] = []
const MAX_PAWS = 10

// easeOutBack 弹性出现
function easeOutBack(t: number) {
  const c1 = 1.70158
  const c3 = c1 + 1
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2)
}

function resize() {
  const el = canvas.value
  if (!el) return
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  el.width = window.innerWidth * dpr
  el.height = window.innerHeight * dpr
  ctx2d = el.getContext('2d')
  ctx2d?.setTransform(dpr, 0, 0, dpr, 0, 0) // 之后按 CSS 像素绘制
}

function spawn(e: PointerEvent) {
  if (reduce || !ctx2d) return

  paws.push({
    x: e.clientX,
    y: e.clientY,
    // v3 · 2026-09-19：在 v2 基础上调大约 25%（绘制时还会 ×1.9，现约 38~67px）
    // v2 · 2026-09-19：整体调小约一半（当时约 30~53px）
    // 历史值（保留备查）：size: 30 + Math.random() * 22, / size: 16 + Math.random() * 12,
    size: 20 + Math.random() * 15,
    angle: (Math.random() - 0.5) * 0.9, // ±~25°，爪印自然朝向
    age: 0,
    life: 1.2,
  })
  if (paws.length > MAX_PAWS) paws.splice(0, paws.length - MAX_PAWS)
  start()
}

/** 画一只猫爪：真实图片 + 点击瞬间的柔和雾圈 */
function drawPaw(p: Paw, scale: number, alpha: number, halo: number) {
  const c = ctx2d
  if (!c) return

  c.save()
  c.translate(p.x, p.y)
  c.rotate(p.angle)
  c.scale(scale, scale)

  // 雾圈（点击瞬间散开的淡淡水汽，纯白渐变）
  if (halo > 0.003) {
    const g = c.createRadialGradient(0, 0, 0, 0, 0, p.size * 1.8)
    g.addColorStop(0, `rgba(255,255,255,${halo * 0.5})`)
    g.addColorStop(1, 'rgba(255,255,255,0)')
    c.globalAlpha = 1
    c.fillStyle = g
    c.beginPath()
    c.arc(0, 0, p.size * 1.8, 0, Math.PI * 2)
    c.fill()
  }

  // 猫爪图片（源图 320×320，主体约占 60%，显示尺寸按比例放大）
  if (pawImg && pawImg.complete && pawImg.naturalWidth > 0) {
    const disp = p.size * 1.9
    c.globalAlpha = alpha
    c.drawImage(pawImg, -disp / 2, -disp / 2, disp, disp)
  }

  c.restore()
}

function frame(now: number) {
  const dt = Math.min((now - last) / 1000, 0.1)
  last = now
  const el = canvas.value
  if (ctx2d && el) ctx2d.clearRect(0, 0, window.innerWidth, window.innerHeight)

  for (let i = paws.length - 1; i >= 0; i--) {
    const p = paws[i]
    if (!p) continue
    p.age += dt
    const t = Math.min(p.age / p.life, 1)

    // 弹性出现 0.3s → 停留 → 淡出上浮
    const appearT = Math.min(p.age / 0.3, 1)
    const fadeT = p.age > 0.45 ? Math.min((p.age - 0.45) / 0.75, 1) : 0
    const scale = 0.3 + easeOutBack(appearT) * 0.7
    const alpha = Math.min(appearT * 2, 1) * (1 - easeOutBack(fadeT)) * (1 - fadeT * fadeT)
    const halo = 0.35 * (1 - Math.min(p.age / 0.55, 1)) * (1 - Math.min(p.age / 0.55, 1))
    const floatY = easeOutBack(fadeT) * 10

    p.y -= floatY * dt * 6 // 淡出时轻微上浮
    drawPaw(p, scale, Math.max(alpha, 0), Math.max(halo, 0))

    if (t >= 1) paws.splice(i, 1)
  }

  if (paws.length > 0) {
    raf = requestAnimationFrame(frame)
  }
  else {
    running = false
    raf = 0
    if (ctx2d && el) ctx2d.clearRect(0, 0, window.innerWidth, window.innerHeight)
  }
}

function start() {
  if (running || !visible) return
  running = true
  last = performance.now()
  raf = requestAnimationFrame(frame)
}

function onVisibility() {
  visible = document.visibilityState === 'visible'
  if (visible) {
    if (paws.length > 0) start()
  }
  else if (raf) {
    cancelAnimationFrame(raf)
    raf = 0
    running = false
  }
}

onMounted(() => {
  reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  // 加载抠图后的透明猫爪（baseURL 兼容 GitHub Pages 子路径部署）
  const { app } = useRuntimeConfig()
  pawImg = new Image()
  pawImg.src = `${app.baseURL}images/paw.png`

  resize()
  window.addEventListener('pointerdown', spawn, { passive: true })
  window.addEventListener('resize', resize)
  document.addEventListener('visibilitychange', onVisibility)
})

onUnmounted(() => {
  window.removeEventListener('pointerdown', spawn)
  window.removeEventListener('resize', resize)
  document.removeEventListener('visibilitychange', onVisibility)
  if (raf) cancelAnimationFrame(raf)
})
</script>
