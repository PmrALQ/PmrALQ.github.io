<template>
  <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
    <BlogCard v-for="post in posts" :key="post._path" :post="post" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  posts: Array<{
    _path: string
    title: string
    description?: string
    date?: string
    tags?: string[]
  }>
}>()
</script>
