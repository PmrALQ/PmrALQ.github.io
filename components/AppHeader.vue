<template>
  <header
    ref="headerRef"
    class="sticky top-0 z-50 glass-nav"
  >
    <div class="mx-auto flex items-center justify-between px-[22px] h-[54px]" style="max-width: var(--max-grid)">
      <!-- Logo -->
      <NuxtLink
        :to="localePath('/')"
        class="flex items-center gap-2 text-decoration-none"
        style="font-size:15px; font-weight:650; letter-spacing:-0.01em; color:var(--text); text-decoration:none;"
      >
        {{ t('siteName') }}
      </NuxtLink>

      <!-- Desktop nav -->
      <div class="hidden items-center gap-1 md:flex">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="px-3 py-1.5 text-sm font-medium rounded-full transition-colors"
          style="color:var(--text-2); text-decoration:none;"
          exact-active-class="!text-[var(--text)]"
          @mouseenter="(e: MouseEvent) => (e.target as HTMLElement).style.color = 'var(--text)'"
          @mouseleave="(e: MouseEvent) => { if (!(e.target as HTMLElement).classList.contains('router-link-exact-active')) (e.target as HTMLElement).style.color = 'var(--text-2)' }"
        >
          {{ t(link.labelKey) }}
        </NuxtLink>
      </div>

      <!-- Right: theme + lang + mobile -->
      <div class="flex items-center gap-3">
        <ThemeToggle />
        <LanguageSwitch />

        <!-- Mobile hamburger -->
        <button
          class="inline-flex items-center justify-center rounded-full p-2 md:hidden"
          style="color:var(--text-2);"
          aria-label="Toggle menu"
          @click="mobileOpen = !mobileOpen"
        >
          <svg
            v-if="!mobileOpen"
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <div
        v-if="mobileOpen"
        class="border-t md:hidden px-[22px] py-3"
        style="background:var(--surface); border-color:var(--hairline);"
      >
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="block rounded-lg px-3 py-2.5 text-sm font-medium"
          style="color:var(--text-2); text-decoration:none;"
          exact-active-class="!text-[var(--text)]"
          @click="mobileOpen = false"
        >
          {{ t(link.labelKey) }}
        </NuxtLink>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()
const mobileOpen = ref(false)
const headerRef = ref<HTMLElement>()

const navLinks = [
  { to: '/', labelKey: 'nav.home' },
  { to: '/about', labelKey: 'nav.about' },
  { to: '/archive', labelKey: 'nav.archive' },
  { to: '/guestbook', labelKey: 'nav.guestbook' },
  { to: '/gallery', labelKey: 'nav.gallery' },
  { to: '/changelog', labelKey: 'nav.changelog' },
]

// Close mobile menu on route change
const route = useRoute()
watch(() => route.fullPath, () => {
  mobileOpen.value = false
})

// Scroll-aware border — only show hairline when scrolled
function onScroll() {
  headerRef.value?.classList.toggle('scrolled', window.scrollY > 8)
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll() // initial state
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.slide-down-enter-active {
  transition: all 0.25s var(--ease-out-quart);
}
.slide-down-leave-active {
  transition: all 0.2s var(--ease-out-quart);
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
