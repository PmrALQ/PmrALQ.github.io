<template>
  <div class="flex min-h-screen flex-col">
    <!-- 全站特效：开屏（仅首访）+ 点击云雾（fixed 定位，不影响布局） -->
    <CloudSplash />
    <ClickClouds />
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
// Layout handles i18n head attributes at page level
</script>
