<template>
  <div class="px-6 py-24">
    <div class="mx-auto max-w-5xl">
      <!-- Page Hero -->
      <PageHero :title="t('gallery.title')" :description="t('gallery.description')" />

      <!-- Photo grid -->
      <div v-if="photos && photos.length > 0" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="photo in photos"
          :key="photo._path || photo.stem"
          class="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md hover:border-primary-300 dark:border-gray-800 dark:bg-gray-900 dark:hover:border-primary-700 cursor-pointer"
          @click="openLightbox(photo.image, photo.title)"
        >
          <div class="aspect-square overflow-hidden bg-gray-100 dark:bg-gray-800">
            <img
              :src="photo.image"
              :alt="photo.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          </div>
          <div class="p-4">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white truncate">
              {{ photo.title }}
            </h3>
            <time v-if="photo.date" class="text-xs text-gray-400 dark:text-gray-500 mt-1">
              {{ formatDate(photo.date) }}
            </time>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <p v-else class="text-center text-gray-500 dark:text-gray-400 py-16">
        {{ t('gallery.noPhotos') }}
      </p>
    </div>

    <!-- Lightbox -->
    <GalleryLightbox
      :visible="lightboxVisible"
      :src="lightboxSrc"
      :alt="lightboxAlt"
      @close="lightboxVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
const { t, locale } = useI18n()

const lightboxVisible = ref(false)
const lightboxSrc = ref('')
const lightboxAlt = ref('')

function openLightbox(src: string, alt: string) {
  lightboxSrc.value = src
  lightboxAlt.value = alt
  lightboxVisible.value = true
}

const { data: photos } = await useAsyncData(
  `gallery-${locale.value}`,
  async () => {
    const results = await queryCollection('gallery')
      .where('path', 'LIKE', `/${locale.value}/gallery/%`)
      .order('date', 'DESC')
      .all()
    return results
  },
  { watch: [locale] }
)

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

useHead({
  title: t('gallery.title'),
  meta: [{ name: 'description', content: t('gallery.description') }],
})
</script>
