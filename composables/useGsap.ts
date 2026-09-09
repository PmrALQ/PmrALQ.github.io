/**
 * Central GSAP setup — register plugins once (module scope).
 * Returns { gsap, ScrollTrigger } for use in components/composables.
 * ScrollTrigger instances must only be created inside onMounted.
 */

import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useGsap() {
  return { gsap, ScrollTrigger }
}
