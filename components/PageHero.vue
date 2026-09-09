<template>
  <div class="mb-12">
    <h1 style="font-size:clamp(27px,5vw,46px); font-weight:700; letter-spacing:-0.03em; line-height:1.1; color:var(--text); text-align:center;">
      {{ title }}
    </h1>
    <p v-if="description" class="mt-4 mx-auto max-w-xl text-center" style="font-size:clamp(15px,2.5vw,18px); color:var(--text-2); line-height:1.6;">
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
