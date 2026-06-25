<template>
  <footer class="border-t border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950">
    <div class="mx-auto flex max-w-5xl flex-col items-center gap-4 px-6 py-10 sm:flex-row sm:justify-between">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        © {{ new Date().getFullYear() }} {{ t('siteName') }}
      </p>
      <div class="flex items-center gap-6">
        <NuxtLink
          v-for="link in footerLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
        >
          {{ t(link.labelKey) }}
        </NuxtLink>
        <SocialLinks />
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const footerLinks = [
  { to: '/', labelKey: 'nav.home' },
  { to: '/blog', labelKey: 'nav.blog' },
  { to: '/about', labelKey: 'nav.about' },
]
</script>
