<template>
  <div class="flex min-h-[60vh] flex-col items-center justify-center px-6 text-center">
    <h1 class="text-6xl font-extrabold text-gray-200 dark:text-gray-800">
      {{ error.statusCode }}
    </h1>
    <h2 class="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
      {{ error.statusCode === 404 ? 'Page Not Found' : 'Something Went Wrong' }}
    </h2>
    <p class="mt-2 text-gray-500 dark:text-gray-400 max-w-md">
      {{ error.statusCode === 404 ? 'The page you are looking for doesn\'t exist or has been moved.' : 'An unexpected error occurred. Please try again later.' }}
    </p>
    <NuxtLink
      to="/"
      class="mt-8 inline-flex items-center rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200 transition-colors"
    >
      ← Back to Home
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  error: {
    statusCode: number
    message: string
  }
}>()

// Clear any previous layout errors
const { error } = toRefs(props)

useHead({
  title: computed(() => error.value.statusCode === 404 ? 'Page Not Found' : 'Error'),
})
</script>
