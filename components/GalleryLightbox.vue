<template>
  <Teleport to="body">
    <Transition name="lightbox">
      <div
        v-if="visible"
        class="fixed inset-0 z-[100] flex items-center justify-center p-8"
        style="background:rgba(0,0,0,0.88);"
        data-cursor="zoom-out"
        @click="$emit('close')"
      >
        <button
          class="absolute top-6 right-6 rounded-full p-2 transition-opacity hover:opacity-70"
          style="color:#fff;"
          @click="$emit('close')"
          aria-label="Close"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <img
          v-if="src"
          :src="src"
          :alt="alt"
          class="max-h-[90vh] max-w-[90vw] rounded-card object-contain"
          @click.stop
        />
        <p v-if="alt" class="absolute bottom-8 text-center text-sm" style="color:var(--text-3);">{{ alt }}</p>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  src: string
  alt?: string
}>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.lightbox-enter-active { transition: opacity 0.3s var(--ease-out-quart); }
.lightbox-leave-active { transition: opacity 0.2s var(--ease-out-quart); }
.lightbox-enter-from,
.lightbox-leave-to { opacity: 0; }
</style>
