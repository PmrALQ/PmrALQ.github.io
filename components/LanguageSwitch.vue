<template>
  <div class="seg-control">
    <button
      v-for="locale in availableLocales"
      :key="locale.code"
      :class="{ active: locale.code === currentLocale }"
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
