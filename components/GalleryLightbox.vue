<template>
  <Teleport to="body">
    <Transition name="lightbox">
      <div
        v-if="visible"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-6"
        @click.self="$emit('close')"
      >
        <!-- Close button -->
        <button
          class="absolute top-6 right-6 text-white/70 hover:text-white text-3xl transition-colors"
          @click="$emit('close')"
          aria-label="Close"
        >
          ✕
        </button>

        <!-- Image -->
        <div class="max-w-5xl max-h-[85vh] w-full">
          <img
            v-if="src"
            :src="src"
            :alt="alt"
            class="w-full h-full object-contain rounded-xl"
          />
          <p v-if="alt" class="text-center text-white/70 mt-4 text-sm">{{ alt }}</p>
        </div>
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
.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.3s ease;
}
.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}
</style>
