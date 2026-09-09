/**
 * Reusable GSAP entrance animation composable.
 * Add `data-animate` to any element that should fade-up on page load.
 * Add `data-animate-delay="0.2"` to override the per-item stagger delay.
 */

import { gsap } from 'gsap'

export function usePageAnimations(rootRef: Ref<HTMLElement | undefined>) {
  let ctx: gsap.Context | null = null

  onMounted(() => {
    if (!rootRef.value) return

    ctx = gsap.context(() => {
      const targets = rootRef.value!.querySelectorAll<HTMLElement>('[data-animate]')
      if (targets.length === 0) return

      // Build stagger array from data attributes
      const elements = Array.from(targets)
      const defaultStagger = 0.08

      elements.forEach((el, i) => {
        const delay = el.dataset.animateDelay
          ? parseFloat(el.dataset.animateDelay)
          : i * defaultStagger

        gsap.from(el, {
          autoAlpha: 0,
          y: 16,
          duration: 0.45,
          delay,
          ease: 'power3.out',
        })
      })
    }, rootRef.value)
  })

  onUnmounted(() => {
    ctx?.revert()
  })
}
