<template>
  <div class="flex justify-center mb-12">
    <div class="seg-control">
      <button
        :class="{ active: active === 'all' }"
        @click="$emit('select', 'all')"
      >
        {{ t('archive.all') }}
      </button>
      <button
        v-for="cat in categories"
        :key="cat.key"
        :class="{ active: active === cat.key }"
        @click="$emit('select', cat.key)"
      >
        {{ cat.label }}
      </button>
    </div>
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

const categories = computed(() => [
  { key: '经验总结', label: t('archive.categories.experience') },
  { key: '算法学习', label: t('archive.categories.algorithm') },
  { key: '作品分享', label: t('archive.categories.project') },
])
</script>
