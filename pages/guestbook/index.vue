<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <!-- Page Hero -->
      <PageHero :title="t('guestbook.title')" :description="t('guestbook.description')" />

      <!-- Coming soon notice -->
      <div class="text-center py-16">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary-50 dark:bg-primary-900/20 mb-6">
          <svg class="w-10 h-10 text-primary-400 dark:text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 9.75a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 01.778-.332 48.294 48.294 0 005.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-3">
          {{ t('guestbook.comingSoon') }}
        </h2>
        <p class="text-gray-500 dark:text-gray-400 max-w-md mx-auto leading-relaxed">
          {{ t('guestbook.walineHint') }}
        </p>
      </div>

      <!-- Waline mount point (reserved for future activation) -->
      <div id="waline" class="mt-8" />
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

useHead({
  title: t('guestbook.title'),
  meta: [{ name: 'description', content: t('guestbook.description') }],
})
</script>
