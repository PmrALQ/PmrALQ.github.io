<template>
  <div ref="pageRoot" class="mx-auto px-[22px] section-gap" style="max-width:var(--max-grid);">
    <div data-animate>
      <PageHero :title="t('gallery.title')" :description="t('gallery.description')" />
    </div>
    <div v-if="photos && photos.length > 0" class="grid gap-[14px]" style="grid-template-columns:repeat(auto-fill, minmax(290px, 1fr));">
      <div
        v-for="(photo, i) in photos"
        :key="photo.src"
        data-animate
        :data-animate-delay="String(0.12 + i * 0.06)"
        class="card-apple overflow-hidden cursor-pointer"
        @click="openLightbox(photo.src, photo.title)"
      >
        <div class="aspect-square overflow-hidden" style="background:var(--hover);">
          <img :src="photo.src" :alt="photo.title" class="w-full h-full object-cover transition-transform duration-500 hover:scale-105" />
        </div>
        <div class="p-4">
          <h3 class="truncate" style="font-size:15px; font-weight:600; letter-spacing:-0.01em; color:var(--text);">{{ photo.title }}</h3>
          <time v-if="photo.date" class="tabular-nums mt-1 block" style="font-size:12px; color:var(--text-3);">{{ formatDate(photo.date) }}</time>
        </div>
      </div>
    </div>

    <p v-else class="text-center py-16" style="color:var(--text-3);">
      {{ t('gallery.noPhotos') }}
    </p>

    <GalleryLightbox :visible="lightboxVisible" :src="lightboxSrc" :alt="lightboxAlt" @close="lightboxVisible = false" />
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()
const pageRoot = ref<HTMLElement>()
usePageAnimations(pageRoot)

const lightboxVisible = ref(false)
const lightboxSrc = ref('')
const lightboxAlt = ref('')

function openLightbox(src: string, alt: string) {
  lightboxSrc.value = src
  lightboxAlt.value = alt
  lightboxVisible.value = true
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  })
}

const { data: photos } = await useFetch('/api/photos')

useHead({
  title: t('gallery.title'),
  meta: [{ name: 'description', content: t('gallery.description') }],
})
</script>
