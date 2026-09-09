<template>
  <footer class="border-t mt-auto" style="border-color:var(--hairline);">
    <div class="mx-auto flex flex-col items-center gap-4 px-[22px] py-8 sm:flex-row sm:justify-between" style="max-width:var(--max-grid)">
      <p class="text-sm" style="color:var(--text-3);">
        © {{ new Date().getFullYear() }} {{ t('siteName') }}
      </p>
      <div class="flex items-center gap-6">
        <NuxtLink
          v-for="link in footerLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="text-sm transition-colors hover:opacity-70"
          style="color:var(--text-3); text-decoration:none;"
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
  { to: '/archive', labelKey: 'nav.archive' },
  { to: '/about', labelKey: 'nav.about' },
]
</script>
