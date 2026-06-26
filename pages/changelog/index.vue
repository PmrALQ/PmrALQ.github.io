<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-3xl">
      <PageHero :title="t('changelog.title')" :description="t('changelog.description')" />
      <div class="space-y-6">
        <ChangelogEntry
          v-for="(entry, index) in entries"
          :key="index"
          :entry="{
            title: entry.title,
            description: entry.description,
            date: entry.date,
            version: entry.version,
            body: entry,
          }"
        />
        <p v-if="entries.length === 0" class="text-center text-gray-400 dark:text-gray-500 py-16">
          还没有版本记录
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()

const { data: entries } = await useAsyncData(`changelog-${locale.value}`, async () => {
  return await queryCollection('content')
    .where('path', 'LIKE', `/${locale.value}/changelog/%`)
    .order('date', 'DESC')
    .all()
}, { watch: [locale] })

useHead({
  title: t('changelog.title'),
  meta: [{ name: 'description', content: t('changelog.description') }],
})
</script>
