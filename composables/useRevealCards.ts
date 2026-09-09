/**
 * 首页 Featured Works 夸张入场：卡片左右交替弹性翻入 + 空闲漂浮。
 * 元素加 `data-reveal-card`（首页专用，其他页面不受影响）。
 */

import { gsap } from 'gsap'

export function useRevealCards(rootRef: Ref<HTMLElement | undefined>) {
  const { ScrollTrigger } = useGsap()
  let ctx: gsap.Context | null = null

  onMounted(() => {
    if (!rootRef.value) return

    ctx = gsap.context(() => {
      const cards = rootRef.value!.querySelectorAll<HTMLElement>('[data-reveal-card]')
      if (cards.length === 0) return

      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      if (reduce) return

      // 预置：左右交替位移 + 3D 翻转，为入场蓄势
      gsap.set(cards, {
        autoAlpha: 0,
        x: (i: number) => (i % 2 ? 90 : -90),
        rotateY: (i: number) => (i % 2 ? -16 : 16),
        rotate: (i: number) => (i % 2 ? 5 : -5),
        transformPerspective: 900,
      })

      // 滚入视口时弹性翻入（back.out 过冲）
      ScrollTrigger.batch(cards, {
        start: 'top 88%',
        once: true,
        onEnter: (els) => {
          gsap.to(els, {
            autoAlpha: 1,
            x: 0,
            rotateY: 0,
            rotate: 0,
            duration: 0.85,
            ease: 'back.out(1.5)',
            stagger: 0.14,
          })
        },
      })

      // 空闲漂浮：只动 y，与入场的 x/rotateY/rotate 无属性冲突
      gsap.to(cards, {
        y: -6,
        duration: 2.4,
        yoyo: true,
        repeat: -1,
        ease: 'sine.inOut',
        stagger: { each: 0.35, yoyo: true },
      })
    }, rootRef.value)

    // 封面图等加载完成后刷新 ScrollTrigger
    window.addEventListener('load', () => ScrollTrigger.refresh(), { once: true })
  })

  onUnmounted(() => {
    ctx?.revert()
  })
}
