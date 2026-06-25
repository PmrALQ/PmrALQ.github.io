<template>
  <div class="mb-16 text-center">
    <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
      {{ title }}
    </h1>
    <p v-if="description" class="mt-4 max-w-2xl mx-auto text-lg text-gray-500 dark:text-gray-400">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>
