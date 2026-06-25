<template>
  <div class="flex items-center gap-1 text-sm font-medium">
    <button
      v-for="locale in availableLocales"
      :key="locale.code"
      class="rounded-md px-2 py-1 transition-colors"
      :class="
        locale.code === currentLocale
          ? 'bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-white'
          : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
      "
      @click="switchLocale(locale.code)"
    >
      {{ locale.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
const { locale, locales, setLocale } = useI18n()

const currentLocale = computed(() => locale.value)

const availableLocales = computed(() =>
  (locales.value as Array<{ code: string; name?: string }>).map((l) => ({
    code: l.code,
    label: l.code === 'zh' ? '中' : 'EN',
  }))
)

async function switchLocale(code: string) {
  await setLocale(code)
}
</script>
