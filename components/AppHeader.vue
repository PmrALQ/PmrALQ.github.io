<template>
  <header
    class="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md dark:border-gray-800 dark:bg-gray-950/80"
  >
    <nav class="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
      <!-- Logo / Site name -->
      <NuxtLink
        :to="localePath('/')"
        class="text-xl font-bold tracking-tight text-gray-900 hover:text-primary-600 dark:text-white dark:hover:text-primary-400 transition-colors"
      >
        {{ t('siteName') }}
      </NuxtLink>

      <!-- Desktop nav -->
      <div class="hidden items-center gap-8 md:flex">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
          exact-active-class="text-primary-600 dark:text-primary-400"
        >
          {{ t(link.labelKey) }}
        </NuxtLink>
      </div>

      <!-- Right side: theme + lang toggle -->
      <div class="flex items-center gap-3">
        <ThemeToggle />
        <LanguageSwitch />

        <!-- Mobile hamburger -->
        <button
          class="inline-flex items-center justify-center rounded-md p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 md:hidden"
          aria-label="Toggle menu"
          @click="mobileOpen = !mobileOpen"
        >
          <svg
            v-if="!mobileOpen"
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
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
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </nav>

    <!-- Mobile menu -->
    <Transition name="slide-down">
      <div
        v-if="mobileOpen"
        class="border-t border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-gray-950 md:hidden"
      >
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-900 dark:hover:text-gray-100"
          exact-active-class="bg-gray-50 text-primary-600 dark:bg-gray-900 dark:text-primary-400"
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

const navLinks = [
  { to: '/', labelKey: 'nav.home' },
  { to: '/blog', labelKey: 'nav.blog' },
  { to: '/about', labelKey: 'nav.about' },
]

// Close mobile menu on route change
const route = useRoute()
watch(() => route.fullPath, () => {
  mobileOpen.value = false
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
