<template>
  <div class="flex flex-wrap justify-center gap-4 mb-12">
    <!-- All button -->
    <button
      class="relative flex flex-col items-center justify-center w-28 h-28 sm:w-32 sm:h-32 rounded-2xl border-2 transition-all duration-300"
      :class="active === 'all'
        ? 'border-primary-500 bg-primary-50 dark:border-primary-400 dark:bg-primary-900/20 shadow-md shadow-primary-100 dark:shadow-primary-900/10'
        : 'border-gray-200 bg-white hover:border-primary-300 hover:bg-primary-50/50 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-primary-600 dark:hover:bg-primary-900/10'"
      @click="$emit('select', 'all')"
    >
      <span class="text-2xl mb-1">📂</span>
      <span class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ t('archive.all') }}</span>
    </button>

    <!-- Category boxes -->
    <button
      v-for="cat in categories"
      :key="cat.key"
      class="relative flex flex-col items-center justify-center w-28 h-28 sm:w-32 sm:h-32 rounded-2xl border-2 transition-all duration-300"
      :class="active === cat.key
        ? 'border-primary-500 bg-primary-50 dark:border-primary-400 dark:bg-primary-900/20 shadow-md shadow-primary-100 dark:shadow-primary-900/10'
        : 'border-gray-200 bg-white hover:border-primary-300 hover:bg-primary-50/50 dark:border-gray-700 dark:bg-gray-900 dark:hover:border-primary-600 dark:hover:bg-primary-900/10'"
      @click="$emit('select', cat.key)"
    >
      <span class="text-2xl mb-1">{{ cat.icon }}</span>
      <span class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ cat.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()

defineProps<{
  active: string
}>()

defineEmits<{
  select: [key: string]
}>()

const categories = [
  { key: '经验总结', icon: '📝', label: t('archive.categories.experience') },
  { key: '算法学习', icon: '🧠', label: t('archive.categories.algorithm') },
  { key: '作品分享', icon: '🎮', label: t('archive.categories.project') },
]
</script>
