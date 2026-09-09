/**
 * 首页卡片 3D 悬停倾斜 + 高光跟随。
 * 元素加 `data-tilt`（作用在 wrapper 上，不与 .card-apple 的 CSS hover 冲突）。
 * 仅精细指针设备启用（触屏跳过），reduced-motion 时停用。
 */

import { gsap } from 'gsap'

export function useTiltCards(rootRef: Ref<HTMLElement | undefined>) {
    let ctx: gsap.Context | null = null
  let listeners: Array<{ el: HTMLElement, move: (e: MouseEvent) => void, leave: () => void }> = []

  onMounted(() => {
    if (!rootRef.value) return
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!fine || reduce) return

    ctx = gsap.context(() => {
      const cards = rootRef.value!.querySelectorAll<HTMLElement>('[data-tilt]')
      cards.forEach((el) => {
        const move = (e: MouseEvent) => {
          const rect = el.getBoundingClientRect()
          const px = (e.clientX - rect.left) / rect.width - 0.5
          const py = (e.clientY - rect.top) / rect.height - 0.5

          gsap.to(el, {
            rotationX: -py * 14,
            rotationY: px * 14,
            transformPerspective: 700,
            duration: 0.3,
            ease: 'power2.out',
            overwrite: 'auto',
          })

          // CSS 变量驱动高光位置（不经过 GSAP，零开销）
          el.style.setProperty('--mx', `${(px + 0.5) * 100}%`)
          el.style.setProperty('--my', `${(py + 0.5) * 100}%`)
        }
        const leave = () => {
          gsap.to(el, {
            rotationX: 0,
            rotationY: 0,
            duration: 0.5,
            ease: 'power2.out',
            overwrite: 'auto',
          })
        }
        el.addEventListener('mousemove', move)
        el.addEventListener('mouseleave', leave)
        listeners.push({ el, move, leave })
      })
    }, rootRef.value)
  })

  onUnmounted(() => {
    // ctx.revert 只清理 gsap 动画，原生监听需手动移除
    for (const l of listeners) {
      l.el.removeEventListener('mousemove', l.move)
      l.el.removeEventListener('mouseleave', l.leave)
    }
    listeners = []
    ctx?.revert()
  })
}
