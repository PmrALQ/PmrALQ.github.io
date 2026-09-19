<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-read);">
    <div data-animate>
      <PageHero :title="t('changelog.title')" :description="t('changelog.description')" />
    </div>
    <div class="space-y-4">
      <div v-for="(entry, index) in entries" :key="index" data-animate :data-animate-delay="String(0.15 + index * 0.06)">
        <ChangelogEntry
          :entry="{
            title: entry.title,
            description: entry.description,
            date: entry.date,
            version: entry.version,
            body: entry,
          }"
        />
      </div>
      <p v-if="entries.length === 0" class="text-center py-16" style="color:var(--text-3);">
        还没有版本记录
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const pageRoot = ref<HTMLElement>()
usePageAnimations(pageRoot)

const { data: entries } = await useAsyncData(`changelog-${locale.value}`, async () => {
  // 修正：原先查 content 集合，而 content 的 schema 不含 version（version 被归入 meta），
  // 导致版本号徽章渲染为空。改查 changelog 集合后 version 为顶层字段，类型也正确。
  // 原写法（保留备查）：return await queryCollection('content')
  return await queryCollection('changelog')
    .where('path', 'LIKE', `/${locale.value}/changelog/%`)
    .order('date', 'DESC')
    .all()
}, { watch: [locale] })

useHead({
  title: t('changelog.title'),
  meta: [{ name: 'description', content: t('changelog.description') }],
})
</script>
